"""
Tests for `schedule_formatting`, the multi-file scheduling loop.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

import black.concurrency as concurrency
from black import Mode, WriteBack
from black.report import Report


def test_formats_all_files_and_reports_counts(tmp_path: Path) -> None:
    unformatted = tmp_path / "a.py"
    unformatted.write_text("x=1\n", encoding="utf8")
    formatted = tmp_path / "b.py"
    formatted.write_text("x = 1\n", encoding="utf8")

    report = Report()

    async def run() -> None:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            await concurrency.schedule_formatting(
                sources={unformatted, formatted},
                fast=False,
                write_back=WriteBack.YES,
                mode=Mode(),
                report=report,
                loop=loop,
                executor=executor,
                no_cache=True,
            )

    asyncio.run(run())

    assert unformatted.read_text(encoding="utf8") == "x = 1\n"
    assert report.change_count == 1
    assert report.same_count == 1
    assert report.failure_count == 0


def test_reports_failed_files_without_aborting_the_run(
    tmp_path: Path, monkeypatch: Any
) -> None:
    sources = {tmp_path / f"test_{i}.py" for i in range(25)}
    for src in sources:
        src.write_text("x = 1\n", encoding="utf8")
    failing = tmp_path / "failing.py"

    def fake_format_file_in_place(
        src: Path,
        fast: bool,
        mode: Mode,
        write_back: WriteBack,
        lock: Optional[object],
    ) -> bool:
        if src == failing:
            raise OSError("no space left on device")
        return False

    monkeypatch.setattr(concurrency, "format_file_in_place", fake_format_file_in_place)

    report = Report()

    async def run() -> None:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            await concurrency.schedule_formatting(
                sources=sources | {failing},
                fast=False,
                write_back=WriteBack.CHECK,
                mode=Mode(),
                report=report,
                loop=loop,
                executor=executor,
                no_cache=True,
            )

    asyncio.run(run())

    # The failing file is reported, and every other file still completes: the
    # scheduling loop must drain all tasks, not stop at the first failure.
    assert report.failure_count == 1
    assert report.same_count == len(sources)
    assert report.change_count == 0
