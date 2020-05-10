# TODO: Remove dependency on click
import io
import sys
import tokenize
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path

import click
from black.defaults import DEFAULT_LINE_LENGTH
from black.formatter import Formatter, Mode, NothingChanged
from black.types import *
from black.util import (color_diff, diff, err, find_project_root, path_empty,
                        wrap_stream_for_windows)

import regex as re
from dataclasses import dataclass, field
from pathspec import PathSpec


def gen_python_files(
    paths: Iterable[Path],
    root: Path,
    include: Optional[Pattern[str]],
    exclude_regexes: Iterable[Pattern[str]],
    report: "Report",
    gitignore: PathSpec,
) -> Iterator[Path]:
    """Generate all files under `path` whose paths are not excluded by the
    `exclude` regex, but are included by the `include` regex.

    Symbolic links pointing outside of the `root` directory are ignored.

    `report` is where output about exclusions goes.
    """
    assert root.is_absolute(), f"INTERNAL ERROR: `root` must be absolute but is {root}"
    for child in paths:
        # Then ignore with `exclude` option.
        try:
            normalized_path = child.resolve().relative_to(root).as_posix()
        except OSError as e:
            report.path_ignored(child, f"cannot be read because {e}")
            continue
        except ValueError:
            if child.is_symlink():
                report.path_ignored(
                    child, f"is a symbolic link that points outside {root}"
                )
                continue

            raise

        # First ignore files matching .gitignore
        if gitignore.match_file(normalized_path):
            report.path_ignored(child, "matches the .gitignore file content")
            continue

        normalized_path = "/" + normalized_path
        if child.is_dir():
            normalized_path += "/"

        is_excluded = False
        for exclude in exclude_regexes:
            exclude_match = exclude.search(normalized_path) if exclude else None
            if exclude_match and exclude_match.group(0):
                report.path_ignored(child, "matches the --exclude regular expression")
                is_excluded = True
                break
        if is_excluded:
            continue

        if child.is_dir():
            yield from gen_python_files(
                child.iterdir(), root, include, exclude_regexes, report, gitignore
            )

        elif child.is_file():
            include_match = include.search(normalized_path) if include else True
            if include_match:
                yield child


class WriteBack(Enum):
    NO = 0
    YES = 1
    DIFF = 2
    CHECK = 3
    COLOR_DIFF = 4

    @classmethod
    def from_configuration(
        cls, *, check: bool, diff: bool, color: bool = False
    ) -> "WriteBack":
        if check and not diff:
            return cls.CHECK

        if diff and color:
            return cls.COLOR_DIFF

        return cls.DIFF if diff else cls.YES


class Changed(Enum):
    NO = 0
    CACHED = 1
    YES = 2


def decode_bytes(src: bytes) -> Tuple[FileContent, Encoding, NewLine]:
    """Return a tuple of (decoded_contents, encoding, newline).

    `newline` is either CRLF or LF but `decoded_contents` is decoded with
    universal newlines (i.e. only contains LF).
    """
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    newline = "\r\n" if b"\r\n" == lines[0][-2:] else "\n"
    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline


def format_file_in_place(
    src: Path,
    fast: bool,
    mode: Mode,
    write_back: WriteBack = WriteBack.NO,
    lock: Any = None,  # multiprocessing.Manager().Lock() is some crazy proxy
) -> bool:
    """Format file under `src` path. Return True if changed.

    If `write_back` is DIFF, write a diff to stdout. If it is YES, write reformatted
    code to the file.
    `mode` and `fast` options are passed to :func:`format_file_contents`.
    """

    @contextmanager
    def nullcontext() -> Iterator[None]:
        """Return an empty context manager.

        To be used like `nullcontext` in Python 3.7.
        """
        yield

    if src.suffix == ".pyi":
        mode = replace(mode, is_pyi=True)

    then = datetime.utcfromtimestamp(src.stat().st_mtime)
    with open(src, "rb") as buf:
        src_contents, encoding, newline = decode_bytes(buf.read())
    try:
        dst_contents = Formatter(mode).format(src_contents, fast=fast)
    except NothingChanged:
        return False

    if write_back == WriteBack.YES:
        with open(src, "w", encoding=encoding, newline=newline) as f:
            f.write(dst_contents)
    elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        now = datetime.utcnow()
        src_name = f"{src}\t{then} +0000"
        dst_name = f"{src}\t{now} +0000"
        diff_contents = diff(src_contents, dst_contents, src_name, dst_name)

        if write_back == write_back.COLOR_DIFF:
            diff_contents = color_diff(diff_contents)

        with lock or nullcontext():
            f = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding=encoding,
                newline=newline,
                write_through=True,
            )
            f = wrap_stream_for_windows(f)
            f.write(diff_contents)
            f.detach()

    return True


# class SourceFile:
#     def __init__(path: Path):
#         self.path = path
#
#     def __hash__(self):
#         return hash(self.path)
#
#     def format_in_place(
#         self,
#         formatter: Formatter,
#         fast: bool,
#         write_back: WriteBack = WriteBack.NO,
#         lock: Any = None,  # multiprocessing.Manager().Lock() is some crazy proxy
#     ) -> bool:
#         """Format file under `src` path. Return True if changed.
#
#         If `write_back` is DIFF, write a diff to stdout. If it is YES, write reformatted
#         code to the file.
#         `mode` and `fast` options are passed to :func:`format_file_contents`.
#         """
#         if src.suffix == ".pyi":
#             formatter.mode = replace(formatter.mode, is_pyi=True)
#
#         then = datetime.utcfromtimestamp(src.stat().st_mtime)
#         with open(src, "rb") as buf:
#             src_contents, encoding, newline = decode_bytes(buf.read())
#         try:
#             dst_contents = format_file_contents(src_contents, fast=fast, mode=mode)
#         except NothingChanged:
#             return False
#
#         if write_back == WriteBack.YES:
#             with open(src, "w", encoding=encoding, newline=newline) as f:
#                 f.write(dst_contents)
#         elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
#             now = datetime.utcnow()
#             src_name = f"{src}\t{then} +0000"
#             dst_name = f"{src}\t{now} +0000"
#             diff_contents = diff(src_contents, dst_contents, src_name, dst_name)
#
#             if write_back == write_back.COLOR_DIFF:
#                 diff_contents = color_diff(diff_contents)
#
#             with lock or nullcontext():
#                 f = io.TextIOWrapper(
#                     sys.stdout.buffer,
#                     encoding=encoding,
#                     newline=newline,
#                     write_through=True,
#                 )
#                 f = wrap_stream_for_windows(f)
#                 f.write(diff_contents)
#                 f.detach()
#
#         return True


def re_compile_maybe_verbose(regex: str) -> Pattern[str]:
    """Compile a regular expression string in `regex`.

    If it contains newlines, use verbose mode.
    """
    if "\n" in regex:
        regex = "(?x)" + regex
    compiled: Pattern[str] = re.compile(regex)
    return compiled


def get_sources(
    *,
    ctx: click.Context,
    src: Tuple[str, ...],
    quiet: bool,
    verbose: bool,
    include: str,
    exclude: str,
    force_exclude: Optional[str],
    report: "Report",
) -> Set[Path]:
    """Compute the set of files to be formatted."""

    def re_compile_maybe_verbose(regex: str) -> Pattern[str]:
        """Compile a regular expression string in `regex`.

        If it contains newlines, use verbose mode.
        """
        if "\n" in regex:
            regex = "(?x)" + regex
        compiled: Pattern[str] = re.compile(regex)
        return compiled

    @lru_cache()
    def get_gitignore(root: Path) -> PathSpec:
        """ Return a PathSpec matching gitignore content if present."""
        gitignore = root / ".gitignore"
        lines: List[str] = []
        if gitignore.is_file():
            with gitignore.open() as gf:
                lines = gf.readlines()
        return PathSpec.from_lines("gitwildmatch", lines)

    try:
        include_regex = re_compile_maybe_verbose(include)
    except re.error:
        err(f"Invalid regular expression for include given: {include!r}")
        ctx.exit(2)
    try:
        exclude_regex = re_compile_maybe_verbose(exclude)
    except re.error:
        err(f"Invalid regular expression for exclude given: {exclude!r}")
        ctx.exit(2)
    try:
        force_exclude_regex = (
            re_compile_maybe_verbose(force_exclude) if force_exclude else None
        )
    except re.error:
        err(f"Invalid regular expression for force_exclude given: {force_exclude!r}")
        ctx.exit(2)

    root = find_project_root(src)
    sources: Set[Path] = set()
    path_empty(src, "No Path provided. Nothing to do 😴", quiet, verbose, ctx)
    exclude_regexes = [exclude_regex]
    if force_exclude_regex is not None:
        exclude_regexes.append(force_exclude_regex)

    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.update(
                gen_python_files(
                    p.iterdir(),
                    root,
                    include_regex,
                    exclude_regexes,
                    report,
                    get_gitignore(root),
                )
            )
        elif s == "-":
            sources.add(p)
        elif p.is_file():
            sources.update(
                gen_python_files(
                    [p], root, None, exclude_regexes, report, get_gitignore(root)
                )
            )
        else:
            err(f"invalid path: {s}")
    return sources
