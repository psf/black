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


def read_data(name: str, data: bool = True) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    if not name.endswith((".py", ".pyi", ".out", ".diff")):
        name += ".py"
    base_dir = DATA_DIR if data else PROJECT_ROOT
    return read_data_from_file(base_dir / name)


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


@contextmanager
def change_directory(path: Path) -> Iterator[None]:
    """Context manager to temporarily chdir to a different directory."""
    previous_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(previous_dir)
