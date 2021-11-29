"""
Note: this module should only be imported if support for formatting multiple
files is needed.
"""
import asyncio
import signal
import sys
import typing

from multiprocessing import Manager
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor
from mypy_extensions import mypyc_attr
from pathlib import Path
from typing import Set, Optional

import black

from black import WriteBack, format_file_in_place, DEFAULT_WORKERS
from black.cache import Cache, read_cache, filter_cached, write_cache
from black.concurrency import cancel, shutdown, maybe_install_uvloop
from black.mode import Mode
from black.report import Changed

if typing.TYPE_CHECKING:
    from black.report import Report


async def schedule_formatting(
    sources: Set[Path],
    fast: bool,
    write_back: WriteBack,
    mode: Mode,
    report: "Report",
    loop: asyncio.AbstractEventLoop,
    executor: Executor,
) -> None:
    """Run formatting of `sources` in parallel using the provided `executor`.

    (Use ProcessPoolExecutors for actual parallelism.)

    `write_back`, `fast`, and `mode` options are passed to
    :func:`format_file_in_place`.
    """
    cache: Cache = {}
    if write_back not in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        cache = read_cache(mode)
        sources, cached = filter_cached(cache, sources)
        for src in sorted(cached):
            report.done(src, Changed.CACHED)
    if not sources:
        return

    cancelled = []
    sources_to_cache = []
    lock = None
    if write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        # For diff output, we need locks to ensure we don't interleave output
        # from different processes.
        manager = Manager()
        lock = manager.Lock()
    tasks = {
        asyncio.ensure_future(
            loop.run_in_executor(
                executor, format_file_in_place, src, fast, mode, write_back, lock
            )
        ): src
        for src in sorted(sources)
    }
    pending = tasks.keys()
    try:
        loop.add_signal_handler(signal.SIGINT, cancel, pending)
        loop.add_signal_handler(signal.SIGTERM, cancel, pending)
    except NotImplementedError:
        # There are no good alternatives for these on Windows.
        pass
    while pending:
        done, _ = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            src = tasks.pop(task)
            if task.cancelled():
                cancelled.append(task)
            elif task.exception():
                report.failed(src, str(task.exception()))
            else:
                changed = Changed.YES if task.result() else Changed.NO
                # If the file was written back or was successfully checked as
                # well-formatted, store this information in the cache.
                if write_back is WriteBack.YES or (
                    write_back is WriteBack.CHECK and changed is Changed.NO
                ):
                    sources_to_cache.append(src)
                report.done(src, changed)
    if cancelled:
        if sys.version_info >= (3, 7):
            await asyncio.gather(*cancelled, return_exceptions=True)
        else:
            await asyncio.gather(*cancelled, loop=loop, return_exceptions=True)
    if sources_to_cache:
        write_cache(cache, sources_to_cache, mode)


# diff-shades depends on being to monkeypatch this function to operate. I know it's
# not ideal, but this shouldn't cause any issues ... hopefully. ~ichard26
@mypyc_attr(patchable=True)
def reformat_many(
    sources: Set[Path],
    fast: bool,
    write_back: WriteBack,
    mode: Mode,
    report: "Report",
    workers: Optional[int],
) -> None:
    """Reformat multiple files using a ProcessPoolExecutor."""
    if black.__BLACK_MAIN_CALLED__:
        maybe_install_uvloop()

    executor: Executor
    loop = asyncio.get_event_loop()
    worker_count = workers if workers is not None else DEFAULT_WORKERS
    if sys.platform == "win32":
        # Work around https://bugs.python.org/issue26903
        assert worker_count is not None
        worker_count = min(worker_count, 60)
    try:
        executor = ProcessPoolExecutor(max_workers=worker_count)
    except (ImportError, NotImplementedError, OSError):
        # we arrive here if the underlying system does not support multi-processing
        # like in AWS Lambda or Termux, in which case we gracefully fallback to
        # a ThreadPoolExecutor with just a single worker (more workers would not do us
        # any good due to the Global Interpreter Lock)
        executor = ThreadPoolExecutor(max_workers=1)

    try:
        loop.run_until_complete(
            schedule_formatting(
                sources=sources,
                fast=fast,
                write_back=write_back,
                mode=mode,
                report=report,
                loop=loop,
                executor=executor,
            )
        )
    finally:
        shutdown(loop)
        if executor is not None:
            executor.shutdown()
