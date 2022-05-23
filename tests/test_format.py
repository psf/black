from dataclasses import replace
from typing import Any, Iterator, List
from unittest.mock import patch

import pytest

import black
from tests.util import (
    DEFAULT_MODE,
    PY36_VERSIONS,
    assert_format,
    dump_to_stderr,
    read_data,
    all_data_cases,
)

# Mirrors the test_format_files target sources in BUILD.pants.
# Update that file if you modify this list.
SOURCES: List[str] = [
    "src/black/__init__.py",
    "src/black/__main__.py",
    "src/black/brackets.py",
    "src/black/cache.py",
    "src/black/comments.py",
    "src/black/concurrency.py",
    "src/black/const.py",
    "src/black/debug.py",
    "src/black/files.py",
    "src/black/linegen.py",
    "src/black/lines.py",
    "src/black/mode.py",
    "src/black/nodes.py",
    "src/black/numerics.py",
    "src/black/output.py",
    "src/black/parsing.py",
    "src/black/report.py",
    "src/black/rusty.py",
    "src/black/strings.py",
    "src/black/trans.py",
    "src/blackd/__init__.py",
    "src/blib2to3/pygram.py",
    "src/blib2to3/pytree.py",
    "src/blib2to3/pgen2/conv.py",
    "src/blib2to3/pgen2/driver.py",
    "src/blib2to3/pgen2/grammar.py",
    "src/blib2to3/pgen2/literals.py",
    "src/blib2to3/pgen2/parse.py",
    "src/blib2to3/pgen2/pgen.py",
    "src/blib2to3/pgen2/tokenize.py",
    "src/blib2to3/pgen2/token.py",
    "setup.py",
    "tests/test_black.py",
    "tests/test_blackd.py",
    "tests/test_format.py",
    "tests/optional.py",
    "tests/util.py",
    "tests/conftest.py",
]


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("black.dump_to_file", dump_to_stderr):
        yield


def check_file(
    subdir: str, filename: str, mode: black.Mode, *, data: bool = True
) -> None:
    source, expected = read_data(subdir, filename, data=data)
    assert_format(source, expected, mode, fast=False)


@pytest.mark.parametrize("filename", all_data_cases("simple_cases"))
def test_simple_format(filename: str) -> None:
    check_file("simple_cases", filename, DEFAULT_MODE)


@pytest.mark.parametrize("filename", all_data_cases("preview"))
def test_preview_format(filename: str) -> None:
    check_file("preview", filename, black.Mode(preview=True))


@pytest.mark.parametrize("filename", all_data_cases("preview_39"))
def test_preview_minimum_python_39_format(filename: str) -> None:
    source, expected = read_data("preview_39", filename)
    mode = black.Mode(preview=True)
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize("filename", SOURCES)
def test_source_is_formatted(filename: str) -> None:
    check_file("", filename, DEFAULT_MODE, data=False)


# =============== #
# Complex cases
# ============= #


def test_empty() -> None:
    source = expected = ""
    assert_format(source, expected)


@pytest.mark.parametrize("filename", all_data_cases("py_36"))
def test_python_36(filename: str) -> None:
    source, expected = read_data("py_36", filename)
    mode = black.Mode(target_versions=PY36_VERSIONS)
    assert_format(source, expected, mode, minimum_version=(3, 6))


@pytest.mark.parametrize("filename", all_data_cases("py_37"))
def test_python_37(filename: str) -> None:
    source, expected = read_data("py_37", filename)
    mode = black.Mode(target_versions={black.TargetVersion.PY37})
    assert_format(source, expected, mode, minimum_version=(3, 7))


@pytest.mark.parametrize("filename", all_data_cases("py_38"))
def test_python_38(filename: str) -> None:
    source, expected = read_data("py_38", filename)
    mode = black.Mode(target_versions={black.TargetVersion.PY38})
    assert_format(source, expected, mode, minimum_version=(3, 8))


@pytest.mark.parametrize("filename", all_data_cases("py_39"))
def test_python_39(filename: str) -> None:
    source, expected = read_data("py_39", filename)
    mode = black.Mode(target_versions={black.TargetVersion.PY39})
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = black.Mode(target_versions={black.TargetVersion.PY310})
    assert_format(source, expected, mode, minimum_version=(3, 10))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310_without_target_version(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = black.Mode()
    assert_format(source, expected, mode, minimum_version=(3, 10))


def test_patma_invalid() -> None:
    source, expected = read_data("miscellaneous", "pattern_matching_invalid")
    mode = black.Mode(target_versions={black.TargetVersion.PY310})
    with pytest.raises(black.parsing.InvalidInput) as exc_info:
        assert_format(source, expected, mode, minimum_version=(3, 10))

    exc_info.match("Cannot parse: 10:11")


@pytest.mark.parametrize("filename", all_data_cases("py_311"))
def test_python_311(filename: str) -> None:
    source, expected = read_data("py_311", filename)
    mode = black.Mode(target_versions={black.TargetVersion.PY311})
    assert_format(source, expected, mode, minimum_version=(3, 11))


@pytest.mark.parametrize("filename", all_data_cases("fast"))
def test_fast_cases(filename: str) -> None:
    source, expected = read_data("fast", filename)
    assert_format(source, expected, fast=True)


def test_python_2_hint() -> None:
    with pytest.raises(black.parsing.InvalidInput) as exc_info:
        assert_format("print 'daylily'", "print 'daylily'")
    exc_info.match(black.parsing.PY2_HINT)


def test_docstring_no_string_normalization() -> None:
    """Like test_docstring but with string normalization off."""
    source, expected = read_data("miscellaneous", "docstring_no_string_normalization")
    mode = replace(DEFAULT_MODE, string_normalization=False)
    assert_format(source, expected, mode)


def test_long_strings_flag_disabled() -> None:
    """Tests for turning off the string processing logic."""
    source, expected = read_data("miscellaneous", "long_strings_flag_disabled")
    mode = replace(DEFAULT_MODE, experimental_string_processing=False)
    assert_format(source, expected, mode)


def test_stub() -> None:
    mode = replace(DEFAULT_MODE, is_pyi=True)
    source, expected = read_data("miscellaneous", "stub.pyi")
    assert_format(source, expected, mode)


def test_power_op_newline() -> None:
    # requires line_length=0
    source, expected = read_data("miscellaneous", "power_op_newline")
    assert_format(source, expected, mode=black.Mode(line_length=0))
