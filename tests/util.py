import os
import sys
import unittest
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Iterator, List, Optional, Tuple

import black
from black.debug import DebugVisitor
from black.mode import TargetVersion
from black.output import diff, err, out

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


def _assert_format_equal(expected: str, actual: str) -> None:
    if actual != expected and not os.environ.get("SKIP_AST_PRINT"):
        bdv: DebugVisitor[Any]
        out("Expected tree:", fg="green")
        try:
            exp_node = black.lib2to3_parse(expected)
            bdv = DebugVisitor()
            list(bdv.visit(exp_node))
        except Exception as ve:
            err(str(ve))
        out("Actual tree:", fg="red")
        try:
            exp_node = black.lib2to3_parse(actual)
            bdv = DebugVisitor()
            list(bdv.visit(exp_node))
        except Exception as ve:
            err(str(ve))

    if actual != expected:
        out(diff(expected, actual, "expected", "actual"))

    assert actual == expected


def assert_format(
    source: str,
    expected: str,
    mode: black.Mode = DEFAULT_MODE,
    *,
    fast: bool = False,
    minimum_version: Optional[Tuple[int, int]] = None,
) -> None:
    """Convenience function to check that Black formats as expected.

    You can pass @minimum_version if you're passing code with newer syntax to guard
    safety guards so they don't just crash with a SyntaxError. Please note this is
    separate from TargetVerson Mode configuration.
    """
    actual = black.format_str(source, mode=mode)
    _assert_format_equal(expected, actual)
    # It's not useful to run safety checks if we're expecting no changes anyway. The
    # assertion right above will raise if reality does actually make changes. This just
    # avoids wasted CPU cycles.
    if not fast and source != expected:
        # Unfortunately the AST equivalence check relies on the built-in ast module
        # being able to parse the code being formatted. This doesn't always work out
        # when checking modern code on older versions.
        if minimum_version is None or sys.version_info >= minimum_version:
            black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode=mode)


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


def read_data(subdir_name: str, name: str, data: bool = True) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    return read_data_from_file(get_case_path(subdir_name, name, data))


def read_data_from_file(file_name: Path) -> Tuple[str, str]:
    with open(file_name, "r", encoding="utf8") as test:
        lines = test.readlines()
    _input: List[str] = []
    _output: List[str] = []
    result = _input
    for line in lines:
        line = line.replace(EMPTY_LINE, "")
        if line.rstrip() == "# output":
            result = _output
            continue

        result.append(line)
    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return "".join(_input).strip() + "\n", "".join(_output).strip() + "\n"


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
