import io
import tempfile
from enum import Enum
from functools import lru_cache, partial
from pathlib import Path
from typing import Iterable, Set, Sized

import click
from black.defaults import DEFAULT_LINE_LENGTH
from black.types import *

from dataclasses import dataclass, field, replace
from mypy_extensions import mypyc_attr

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


@lru_cache()
def find_project_root(srcs: Iterable[str]) -> Path:
    """Return a directory containing .git, .hg, or pyproject.toml.

    That directory can be one of the directories passed in `srcs` or their
    common parent.

    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.
    """
    if not srcs:
        return Path("/").resolve()

    common_base = min(Path(src).resolve() for src in srcs)
    if common_base.is_dir():
        # Append a fake file so `parents` below returns `common_base_dir`, too.
        common_base /= "fake-file"
    for directory in common_base.parents:
        if (directory / ".git").exists():
            return directory

        if (directory / ".hg").is_dir():
            return directory

        if (directory / "pyproject.toml").is_file():
            return directory

    return directory


def path_empty(
    src: Sized, msg: str, quiet: bool, verbose: bool, ctx: click.Context
) -> None:
    """
    Exit if there is no `src` provided for formatting
    """
    if len(src) == 0:
        if verbose or not quiet:
            out(msg)
            ctx.exit(0)


@mypyc_attr(patchable=True)
def dump_to_file(*output: str) -> str:
    """Dump `output` to a temporary file. Return path to the file."""
    with tempfile.NamedTemporaryFile(
        mode="w", prefix="blk_", suffix=".log", delete=False, encoding="utf8"
    ) as f:
        for lines in output:
            f.write(lines)
            if lines and lines[-1] != "\n":
                f.write("\n")
    return f.name


def diff(a: str, b: str, a_name: str, b_name: str) -> str:
    """Return a unified diff string between strings `a` and `b`."""
    import difflib

    a_lines = [line + "\n" for line in a.splitlines()]
    b_lines = [line + "\n" for line in b.splitlines()]
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5)
    )


# TODO: Use ansimarkup
def color_diff(contents: str) -> str:
    """Inject the ANSI color codes to the diff."""
    lines = contents.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("+++") or line.startswith("---"):
            line = "\033[1;37m" + line + "\033[0m"  # bold white, reset
        if line.startswith("@@"):
            line = "\033[36m" + line + "\033[0m"  # cyan, reset
        if line.startswith("+"):
            line = "\033[32m" + line + "\033[0m"  # green, reset
        elif line.startswith("-"):
            line = "\033[31m" + line + "\033[0m"  # red, reset
        lines[i] = line
    return "\n".join(lines)


def wrap_stream_for_windows(
    f: io.TextIOWrapper,
) -> Union[io.TextIOWrapper, "colorama.AnsiToWin32.AnsiToWin32"]:
    """
    Wrap the stream in colorama's wrap_stream so colors are shown on Windows.

    If `colorama` is not found, then no change is made. If `colorama` does
    exist, then it handles the logic to determine whether or not to change
    things.
    """
    try:
        from colorama import initialise

        # We set `strip=False` so that we can don't have to modify
        # test_express_diff_with_color.
        f = initialise.wrap_stream(
            f, convert=None, strip=False, autoreset=False, wrap=True
        )

        # wrap_stream returns a `colorama.AnsiToWin32.AnsiToWin32` object
        # which does not have a `detach()` method. So we fake one.
        f.detach = lambda *args, **kwargs: None  # type: ignore
    except ImportError:
        pass

    return f
