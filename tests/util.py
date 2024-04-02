import argparse
import functools
import os
import shlex
import sys
import unittest
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from functools import partial
from pathlib import Path
from typing import Any, Collection, Iterator, List, Optional, Tuple

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
}

DEFAULT_MODE = black.Mode()
ff = partial(black.format_file_in_place, mode=DEFAULT_MODE, fast=True)
fs = partial(black.format_str, mode=DEFAULT_MODE)


@dataclass
class TestCaseArgs:
    mode: black.Mode = field(default_factory=black.Mode)
    fast: bool = False
    minimum_version: Optional[Tuple[int, int]] = None
    lines: Collection[Tuple[int, int]] = ()
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
    minimum_version: Optional[Tuple[int, int]] = None,
    lines: Collection[Tuple[int, int]] = (),
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
    expected: Optional[str] = None,
    mode: black.Mode = DEFAULT_MODE,
    *,
    fast: bool = False,
    minimum_version: Optional[Tuple[int, int]] = None,
    lines: Collection[Tuple[int, int]] = (),
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


def all_data_cases(subdir_name: str, data: bool = True) -> List[str]:
    cases_dir = get_base_dir(data) / subdir_name
    assert cases_dir.is_dir()
    return [case_path.stem for case_path in cases_dir.iterdir()]


def get_case_path(
    subdir_name: str, name: str, data: bool = True, suffix: str = PYTHON_SUFFIX
) -> Path:
    """Get case path from name"""
    case_path = get_base_dir(data) / subdir_name / name
    if not name.endswith(ALLOWED_SUFFIXES):
        case_path = case_path.with_suffix(suffix)
    assert case_path.is_file(), f"{case_path} is not a file."
    return case_path


def read_data_with_mode(
    subdir_name: str, name: str, data: bool = True
) -> Tuple[TestCaseArgs, str, str]:
    """read_data_with_mode('test_name') -> Mode(), 'input', 'output'"""
    return read_data_from_file(get_case_path(subdir_name, name, data))


def read_data(subdir_name: str, name: str, data: bool = True) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    _, input, output = read_data_with_mode(subdir_name, name, data)
    return input, output


def _parse_minimum_version(version: str) -> Tuple[int, int]:
    major, minor = version.split(".")
    return int(major), int(minor)


@functools.lru_cache()
def get_flags_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target-version",
        action="append",
        type=lambda val: TargetVersion[val.upper()],
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
            " set, the test case will be run twice: once with the specified"
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


def read_data_from_file(file_name: Path) -> Tuple[TestCaseArgs, str, str]:
    with open(file_name, "r", encoding="utf8") as test:
        lines = test.readlines()
    _input: List[str] = []
    _output: List[str] = []
    result = _input
    mode = TestCaseArgs()
    for line in lines:
        if not _input and line.startswith("# flags: "):
            mode = parse_mode(line[len("# flags: ") :])
            if mode.lines:
                # Retain the `# flags: ` line when using --line-ranges=. This requires
                # the `# output` section to also include this line, but retaining the
                # line is important to make the line ranges match what you see in the
                # test file.
                result.append(line)
            continue
        line = line.replace(EMPTY_LINE, "")
        if line.rstrip() == "# output":
            result = _output
            continue

        result.append(line)
    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return mode, "".join(_input).strip() + "\n", "".join(_output).strip() + "\n"


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
