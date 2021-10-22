# coding=utf8

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from shutil import rmtree, which
from tempfile import gettempdir
from typing import Any, List, Optional, Union

import click

from black_primer import lib

# If our environment has uvloop installed lets use it
try:
    import uvloop

    uvloop.install()
except ImportError:
    pass


DEFAULT_CONFIG = Path(__file__).parent / "primer.json"
_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
DEFAULT_WORKDIR = Path(gettempdir()) / f"primer.{_timestamp}"
LOG = logging.getLogger(__name__)
DEFAULT_CONFIG_CONTENTS = json.load(open(DEFAULT_CONFIG))
DEFAULT_PROJECTS = sorted(DEFAULT_CONFIG_CONTENTS["projects"].keys())


def _handle_debug(
    ctx: Optional[click.core.Context],
    param: Optional[Union[click.core.Option, click.core.Parameter]],
    debug: Union[bool, int, str],
) -> Union[bool, int, str]:
    """Turn on debugging if asked otherwise INFO default"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )
    return debug


def _projects_callback(
    ctx: click.core.Context,
    param: Optional[Union[click.core.Option, click.core.Parameter]],
    projects: str,
) -> List[str]:
    requested_projects = set(projects.split(","))

    if str(DEFAULT_CONFIG) == ctx.params["config"]:
        available_projects = set(DEFAULT_PROJECTS)
    else:
        available_projects = set(
            json.load(open(ctx.params["config"]))["projects"].keys()
        )

    unavailable = requested_projects - available_projects
    if unavailable:
        LOG.error(f"Projects not found: {unavailable}. Available: {available_projects}")

    return sorted(requested_projects & available_projects)


async def async_main(
    config: str,
    debug: bool,
    keep: bool,
    long_checkouts: bool,
    no_diff: bool,
    projects: List[str],
    rebase: bool,
    workdir: str,
    workers: int,
) -> int:
    work_path = Path(workdir)
    if not work_path.exists():
        LOG.debug(f"Creating {work_path}")
        work_path.mkdir()

    if not which("black"):
        LOG.error("Can not find 'black' executable in PATH. No point in running")
        return -1

    try:
        ret_val = await lib.process_queue(
            config,
            work_path,
            workers,
            projects,
            keep,
            long_checkouts,
            rebase,
            no_diff,
        )
        return int(ret_val)
    finally:
        if not keep and work_path.exists():
            LOG.debug(f"Removing {work_path}")
            rmtree(work_path, onerror=lib.handle_PermissionError)

    return -2


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-c",
    "--config",
    default=str(DEFAULT_CONFIG),
    type=click.Path(exists=True),
    show_default=True,
    help="JSON config file path",
    # Eager - because config path is used by other callback options
    is_eager=True,
)
@click.option(
    "--debug",
    is_flag=True,
    callback=_handle_debug,
    show_default=True,
    help="Turn on debug logging",
)
@click.option(
    "-k",
    "--keep",
    is_flag=True,
    show_default=True,
    help="Keep workdir + repos post run",
)
@click.option(
    "-L",
    "--long-checkouts",
    is_flag=True,
    show_default=True,
    help="Pull big projects to test",
)
@click.option(
    "--no-diff",
    is_flag=True,
    show_default=True,
    help="Disable showing source file changes in black output",
)
@click.option(
    "--projects",
    default=",".join(DEFAULT_PROJECTS),
    callback=_projects_callback,
    show_default=True,
    help="Comma separated list of projects to run",
)
@click.option(
    "-R",
    "--rebase",
    is_flag=True,
    show_default=True,
    help="Rebase project if already checked out",
)
@click.option(
    "-w",
    "--workdir",
    default=str(DEFAULT_WORKDIR),
    type=click.Path(exists=False),
    show_default=True,
    help="Directory path for repo checkouts",
)
@click.option(
    "-W",
    "--workers",
    default=2,
    type=int,
    show_default=True,
    help="Number of parallel worker coroutines",
)
@click.pass_context
def main(ctx: click.core.Context, **kwargs: Any) -> None:
    """primer - prime projects for blackening... 🏴"""
    LOG.debug(f"Starting {sys.argv[0]}")
    # TODO: Change to asyncio.run when Black >= 3.7 only
    loop = asyncio.get_event_loop()
    try:
        ctx.exit(loop.run_until_complete(async_main(**kwargs)))
    finally:
        loop.close()


if __name__ == "__main__":  # pragma: nocover
    main()
