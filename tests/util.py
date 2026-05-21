import argparse
import functools
import os
import re
import shlex
import sys
import unittest
from collections.abc import Collection, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from functools import partial
from pathlib import Path
from typing import Any

import black
from black.const import DEFAULT_LINE_LENGTH
from black.debug import DebugVisitor
from black.mode import TargetVersion
from black.output import diff, err, out
from black.ranges import parse_line_ranges

from . import conftest

PYTHON_SUFFIX = ".py"
ALLOWED_SUFFIXES = (PYTHON_SUFFIX, ".pyi", ".out", ".diff", ".ipynb")

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR / "data"
PROJECT_ROOT = THIS_DIR.parent
EMPTY_LINE = "# EMPTY LINE WITH WHITESPACE" + " (this comment will be removed)"
DETERMINISTIC_HEADER = "[Deterministic header]"

PY36_VERSIONS = {
    TargetVersion.PY36,
    TargetVersion.PY37,
    TargetVersion.PY38,
    TargetVersion.PY39,
    TargetVersion.PY315,
}

DEFAULT_MODE = black.Mode()
ff = partial(black.format_file_in_place, mode=DEFAULT_MODE, fast=True)
fs = partial(black.format_str, mode=DEFAULT_MODE)


@dataclass
class TestCaseArgs:
    mode: black.Mode = field(default_factory=black.Mode)
    fast: bool = False
    minimum_version: tuple[int, int] | None = None
    lines: Collection[tuple[int, int]] = ()
    no_preview_line_length_1: bool = False


def _assert_format_equal(expected: str, actual: str) -> None:
    if actual != expected and (conftest.PRINT_FULL_TREE or conftest.PRINT_TREE_DIFF):
        bdv: DebugVisitor[Any]
        actual_out: str = ""
        expected_out: str = ""
        if conftest.PRINT_FULL_TREE:
            out("Expected tree:", fg="green")
        try:
            exp_node = black.lib2to3_parse(expected)
            bdv = DebugVisitor(print_output=conftest.PRINT_FULL_TREE)
            list(bdv.visit(exp_node))
            expected_out = "\n".join(bdv.list_output)
        except Exception as ve:
            err(str(ve))
        if conftest.PRINT_FULL_TREE:
            out("Actual tree:", fg="red")
        try:
            exp_node = black.lib2to3_parse(actual)
            bdv = DebugVisitor(print_output=conftest.PRINT_FULL_TREE)
            list(bdv.visit(exp_node))
            actual_out = "\n".join(bdv.list_output)
        except Exception as ve:
            err(str(ve))
        if conftest.PRINT_TREE_DIFF:
            out("Tree Diff:")
            out(
                diff(expected_out, actual_out, "expected tree", "actual tree")
                or "Trees do not differ"
            )

    if actual != expected:
        out(diff(expected, actual, "expected", "actual"))

    assert actual == expected


class FormatFailure(Exception):
    """Used to wrap failures when assert_format() runs in an extra mode."""


def assert_format(
    source: str,
    expected: str,
    mode: black.Mode = DEFAULT_MODE,
    *,
    fast: bool = False,
    minimum_version: tuple[int, int] | None = None,
    lines: Collection[tuple[int, int]] = (),
    no_preview_line_length_1: bool = False,
) -> None:
    """Convenience function to check that Black formats as expected.

    You can pass @minimum_version if you're passing code with newer syntax to guard
    safety guards so they don't just crash with a SyntaxError. Please note this is
    separate from TargetVerson Mode configuration.
    """
    _assert_format_inner(
        source, expected, mode, fast=fast, minimum_version=minimum_version, lines=lines
    )

    # For both preview and non-preview tests, ensure that Black doesn't crash on
    # this code, but don't pass "expected" because the precise output may differ.
    try:
        if mode.unstable:
            new_mode = replace(mode, unstable=False, preview=False)
        else:
            new_mode = replace(mode, preview=not mode.preview)
        _assert_format_inner(
            source,
            None,
            new_mode,
            fast=fast,
            minimum_version=minimum_version,
            lines=lines,
        )
    except Exception as e:
        text = (
            "unstable"
            if mode.unstable
            else "non-preview" if mode.preview else "preview"
        )
        raise FormatFailure(
            f"Black crashed formatting this case in {text} mode."
        ) from e
    # Similarly, setting line length to 1 is a good way to catch
    # stability bugs. Some tests are known to be broken in preview mode with line length
    # of 1 though, and have marked that with a flag --no-preview-line-length-1
    preview_modes = [False]
    if not no_preview_line_length_1:
        preview_modes.append(True)

    for preview_mode in preview_modes:

        try:
            _assert_format_inner(
                source,
                None,
                replace(mode, preview=preview_mode, line_length=1, unstable=False),
                fast=fast,
                minimum_version=minimum_version,
                lines=lines,
            )
        except Exception as e:
            text = "preview" if preview_mode else "non-preview"
            raise FormatFailure(
                f"Black crashed formatting this case in {text} mode with line-length=1."
            ) from e


def _assert_format_inner(
    source: str,
    expected: str | None = None,
    mode: black.Mode = DEFAULT_MODE,
    *,
    fast: bool = False,
    minimum_version: tuple[int, int] | None = None,
    lines: Collection[tuple[int, int]] = (),
) -> None:
    actual = black.format_str(source, mode=mode, lines=lines)
    if expected is not None:
        _assert_format_equal(expected, actual)
    # It's not useful to run safety checks if we're expecting no changes anyway. The
    # assertion right above will raise if reality does actually make changes. This just
    # avoids wasted CPU cycles.
    if not fast and source != actual:
        # Unfortunately the AST equivalence check relies on the built-in ast module
        # being able to parse the code being formatted. This doesn't always work out
        # when checking modern code on older versions.
        if minimum_version is None or sys.version_info >= minimum_version:
            black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode=mode, lines=lines)


def dump_to_stderr(*output: str) -> str:
    return "\n" + "\n".join(output) + "\n"


class BlackBaseTestCase(unittest.TestCase):
    def assertFormatEqual(self, expected: str, actual: str) -> None:
        _assert_format_equal(expected, actual)


def get_base_dir(data: bool) -> Path:
    return DATA_DIR if data else PROJECT_ROOT


CaseId = str | tuple[str, str]


def _parse_minimum_version(version: str) -> tuple[int, int]:
    major, minor = version.split(".")
    return int(major), int(minor)


@functools.lru_cache
def get_flags_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target-version",
        action="store",
        type=lambda val: (TargetVersion[val.upper()],),
        default=(),
    )
    parser.add_argument("--line-length", default=DEFAULT_LINE_LENGTH, type=int)
    parser.add_argument(
        "--skip-string-normalization", default=False, action="store_true"
    )
    parser.add_argument("--pyi", default=False, action="store_true")
    parser.add_argument("--ipynb", default=False, action="store_true")
    parser.add_argument(
        "--skip-magic-trailing-comma", default=False, action="store_true"
    )
    parser.add_argument("--preview", default=False, action="store_true")
    parser.add_argument("--unstable", default=False, action="store_true")
    parser.add_argument("--fast", default=False, action="store_true")
    parser.add_argument(
        "--minimum-version",
        type=_parse_minimum_version,
        default=None,
        help=(
            "Minimum version of Python where this test case is parseable. If this is"
            " set, the test case will be run twice: once without the specified"
            " --target-version, and once with --target-version set to exactly the"
            " specified version. This ensures that Black's autodetection of the target"
            " version works correctly."
        ),
    )
    parser.add_argument("--line-ranges", action="append")
    parser.add_argument(
        "--no-preview-line-length-1",
        default=False,
        action="store_true",
        help=(
            "Don't run in preview mode with --line-length=1, as that's known to cause a"
            " crash"
        ),
    )
    return parser


def parse_mode(flags_line: str) -> TestCaseArgs:
    parser = get_flags_parser()
    args = parser.parse_args(shlex.split(flags_line))
    mode = black.Mode(
        target_versions=set(args.target_version),
        line_length=args.line_length,
        string_normalization=not args.skip_string_normalization,
        is_pyi=args.pyi,
        is_ipynb=args.ipynb,
        magic_trailing_comma=not args.skip_magic_trailing_comma,
        preview=args.preview,
        unstable=args.unstable,
    )
    if args.line_ranges:
        lines = parse_line_ranges(args.line_ranges)
    else:
        lines = []
    return TestCaseArgs(
        mode=mode,
        fast=args.fast,
        minimum_version=args.minimum_version,
        lines=lines,
        no_preview_line_length_1=args.no_preview_line_length_1,
    )


def _parse_cell_body(
    lines: list[str],
    file_flags: str = "",
) -> tuple[TestCaseArgs, str, str, int | None]:
    """Parse one cell (or whole-file) body. Returns mode, input, output, and
    the 0-based index into ``lines`` of the ``# output`` marker (or None for
    idempotency cells).

    ``file_flags`` carries an optional multi-cell file-level ``# flags: ``
    string (already stripped of the ``# flags: `` prefix and trailing
    newline). It is concatenated *before* the cell's own ``# flags: `` line,
    so scalar/store flags follow later-wins (cell beats file). ``--line-ranges``
    is rejected at the file level by ``_extract_file_flags`` and so only ever
    appears here from a cell.
    """
    _input: list[str] = []
    _output: list[str] = []
    result = _input
    output_offset: int | None = None
    cell_flags: str | None = None
    cell_flag_line: str | None = None
    for idx, line in enumerate(lines):
        if not _input and cell_flags is None:
            if not line.strip():
                # Tolerate leading blank lines before the optional `# flags: `
                # line (or before the first content line, when no flags are
                # set). Matches the doc's "first non-blank line" promise.
                continue
            if line.startswith("# flags: "):
                cell_flags = line[len("# flags: ") :].rstrip("\n")
                cell_flag_line = line
                continue
        line = line.replace(EMPTY_LINE, "")
        if line.rstrip() == "# output":
            output_offset = idx
            result = _output
            continue

        result.append(line)

    if cell_flags is not None or file_flags:
        combined = f"{file_flags} {cell_flags or ''}".strip()
        mode = parse_mode(combined)
    else:
        mode = TestCaseArgs()

    if cell_flag_line is not None and mode.lines:
        # Retain the cell's `# flags: ` line when --line-ranges is in effect so
        # the input's line numbers match the ranges. Output must include the
        # same line; that's a fixture-author responsibility.
        _input.insert(0, cell_flag_line)

    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return (
        mode,
        "".join(_input).strip() + "\n",
        "".join(_output).strip() + "\n",
        output_offset,
    )


def read_data_from_file(file_name: Path) -> tuple[TestCaseArgs, str, str]:
    with open(file_name, encoding="utf8") as test:
        lines = test.readlines()
    mode, input_text, output_text, _ = _parse_cell_body(lines)
    return mode, input_text, output_text


CELL_HEADER_RE = re.compile(r"^\[case ([A-Za-z_][A-Za-z0-9_]*)\]$")
FILE_FLAGS_RE = re.compile(r"^# flags: (.*)$")


@dataclass(frozen=True)
class Cell:
    name: str
    args: TestCaseArgs
    input: str
    output: str
    header_lineno: int
    output_lineno: int | None


def is_multi_cell(lines: list[str]) -> bool:
    for line in lines:
        rstripped = line.rstrip()
        if not rstripped:
            continue
        if rstripped.startswith("#"):
            continue
        return bool(CELL_HEADER_RE.match(rstripped))
    return False


def _build_cell(
    name: str,
    header_lineno: int,
    block_start: int,
    body_lines: list[str],
    file_flags: str = "",
) -> Cell:
    args, input_text, output_text, output_offset = _parse_cell_body(
        body_lines, file_flags=file_flags
    )
    output_lineno = block_start + output_offset if output_offset is not None else None
    return Cell(
        name=name,
        args=args,
        input=input_text,
        output=output_text,
        header_lineno=header_lineno,
        output_lineno=output_lineno,
    )


def _extract_file_flags(lines: list[str], path: Path) -> str:
    """Pull a top-level ``# flags: ...`` line from the prose region before the
    first ``[case ]`` header. At most one such line is allowed; multiples
    raise. Returns the flag string (without the ``# flags: `` prefix), or an
    empty string if none is present.
    """
    found: str | None = None
    found_lineno: int = 0
    for idx, line in enumerate(lines, start=1):
        if CELL_HEADER_RE.match(line.rstrip()):
            break
        match = FILE_FLAGS_RE.match(line.rstrip("\n"))
        if not match:
            continue
        if found is not None:
            raise ValueError(
                f"{path}: multiple top-level `# flags: ` lines"
                f" (first at line {found_lineno}, again at line {idx});"
                " only one is allowed"
            )
        found = match.group(1)
        found_lineno = idx
    if found is None:
        return ""
    # Parse-validate at file load time so a malformed top-level surfaces with
    # the file path attached, not buried in a per-cell argparse trace.
    try:
        parsed = parse_mode(found)
    except SystemExit as exc:
        raise ValueError(
            f"{path}: malformed top-level `# flags: ` on line {found_lineno}:"
            f" {found!r}"
        ) from exc
    if parsed.lines:
        raise ValueError(
            f"{path}: `--line-ranges` is not allowed at the file level"
            f" (line {found_lineno}). Line numbers are per-cell, so a"
            " file-level range would apply to every cell against unrelated"
            " content. Set `--line-ranges` inside the relevant `[case ]`"
            " instead."
        )
    return found


def parse_cells(text: str, path: Path) -> list[Cell] | None:
    """Parse a multi-cell fixture file.

    Returns a list of Cell instances, or None if the file is single-case
    (its first non-blank non-comment line is not a `[case <name>]` header).
    Header lines tolerate trailing whitespace; everything else — including
    leading whitespace — is rejected.
    """
    lines = text.splitlines(keepends=True)
    if not is_multi_cell(lines):
        return None

    file_flags = _extract_file_flags(lines, path)

    cells: list[Cell] = []
    current_name: str | None = None
    current_header_lineno: int = 0
    current_lines: list[str] = []
    current_block_start: int = 0  # 1-based line number of first cell content line

    for idx, line in enumerate(lines, start=1):
        match = CELL_HEADER_RE.match(line.rstrip())
        if match:
            if current_name is not None:
                cells.append(
                    _build_cell(
                        current_name,
                        current_header_lineno,
                        current_block_start,
                        current_lines,
                        file_flags=file_flags,
                    )
                )
            current_name = match.group(1)
            current_header_lineno = idx
            current_lines = []
            current_block_start = idx + 1
        else:
            if current_name is not None:
                current_lines.append(line)

    if current_name is not None:
        cells.append(
            _build_cell(
                current_name,
                current_header_lineno,
                current_block_start,
                current_lines,
                file_flags=file_flags,
            )
        )

    assert cells, (
        f"unreachable: {path}: is_multi_cell said yes but no `[case ]`"
        " headers were parsed"
    )

    seen: dict[str, int] = {}
    for cell in cells:
        if cell.name in seen:
            raise ValueError(
                f"Duplicate cell name `{cell.name}` in {path}:"
                f" first at line {seen[cell.name]}, again at line"
                f" {cell.header_lineno}"
            )
        seen[cell.name] = cell.header_lineno

    return cells


@functools.lru_cache(maxsize=None)
def try_parse_cells(case_path: Path) -> tuple[Cell, ...] | None:
    """Parse cells from `case_path`, cached on file path.

    Returns None for single-case files; returns an immutable tuple of cells for
    multi-cell files. Cache is keyed on Path equality and lives for the whole
    test process — file edits during a single run won't be picked up.
    """
    if case_path.suffix not in (PYTHON_SUFFIX, ".pyi"):
        return None
    try:
        text = case_path.read_text(encoding="utf8")
    except (OSError, UnicodeDecodeError):
        return None
    cells = parse_cells(text, case_path)
    if cells is None:
        return None
    return tuple(cells)


def find_cell(case_path: Path, cell_name: str) -> Cell | None:
    """Return the named cell from a multi-cell fixture, or None if missing.

    Returns None for single-case files.
    """
    cells = try_parse_cells(case_path)
    if cells is None:
        return None
    for cell in cells:
        if cell.name == cell_name:
            return cell
    return None


def all_data_cases(subdir_name: str, data: bool = True) -> list[CaseId]:
    """Discover test cases under `subdir_name`.

    Single-case files contribute one `stem` entry; multi-cell files contribute
    one `(stem, cell_name)` tuple per `[case <name>]` cell.
    """
    cases_dir = get_base_dir(data) / subdir_name
    assert cases_dir.is_dir()
    result: list[CaseId] = []
    for case_path in cases_dir.iterdir():
        if not case_path.is_file():
            continue
        # test_simple_format only consumes .py/.pyi fixtures; .diff/.out/.ipynb
        # files are loaded by name (with extension) by other tests.
        if case_path.suffix not in (PYTHON_SUFFIX, ".pyi"):
            continue
        cells = try_parse_cells(case_path)
        if cells is None:
            result.append(case_path.stem)
        else:
            for cell in cells:
                result.append((case_path.stem, cell.name))
    return result


def _normalize_case(name: CaseId) -> tuple[str, str | None]:
    """Split a `CaseId` into `(stem, cell_name_or_None)`.

    Centralizes the union-discrimination so callers don't sprinkle
    `isinstance(name, tuple)` everywhere.
    """
    if isinstance(name, tuple):
        return name[0], name[1]
    return name, None


def get_case_path(
    subdir_name: str,
    stem: str,
    data: bool = True,
    suffix: str = PYTHON_SUFFIX,
) -> Path:
    """Get case path from a bare stem."""
    case_path = get_base_dir(data) / subdir_name / stem
    if not stem.endswith(ALLOWED_SUFFIXES):
        case_path = case_path.with_suffix(suffix)
    assert case_path.is_file(), f"{case_path} is not a file."
    return case_path


def read_data_with_mode(
    subdir_name: str, name: CaseId, data: bool = True
) -> tuple[TestCaseArgs, str, str]:
    """read_data_with_mode('test_name') -> Mode(), 'input', 'output'.

    `name` is either a bare stem (legacy single-case) or a `(stem, cell_name)`
    tuple (multi-cell). Calling with a bare stem on a multi-cell file is an
    error — there is no well-defined "whole-file" view of a multi-cell
    fixture.
    """
    stem, cell_name = _normalize_case(name)
    path = get_case_path(subdir_name, stem, data)
    cells = try_parse_cells(path)
    if cell_name is not None:
        if cells is None:
            raise AssertionError(
                f"{path}: requested cell `{cell_name}` but file is single-case."
            )
        for cell in cells:
            if cell.name == cell_name:
                return cell.args, cell.input, cell.output
        raise AssertionError(f"{path}: no cell named `{cell_name}`.")
    if cells is not None:
        raise AssertionError(
            f"{path}: bare-stem read of a multi-cell file is not supported."
            " Use a (stem, cell_name) tuple to address a specific cell."
        )
    return read_data_from_file(path)


def read_data(
    subdir_name: str, name: CaseId, data: bool = True
) -> tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    _, input, output = read_data_with_mode(subdir_name, name, data)
    return input, output


def read_jupyter_notebook(subdir_name: str, name: str, data: bool = True) -> str:
    return read_jupyter_notebook_from_file(
        get_case_path(subdir_name, name, data, suffix=".ipynb")
    )


def read_jupyter_notebook_from_file(file_name: Path) -> str:
    with open(file_name, mode="rb") as fd:
        content_bytes = fd.read()
    return content_bytes.decode()


@contextmanager
def change_directory(path: Path) -> Iterator[None]:
    """Context manager to temporarily chdir to a different directory."""
    previous_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(previous_dir)
