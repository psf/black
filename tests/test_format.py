from dataclasses import replace
from typing import Any, Iterator, List
from unittest.mock import patch

import pytest

import black
from tests.util import (
    DEFAULT_MODE,
    PY36_VERSIONS,
    THIS_DIR,
    assert_format,
    dump_to_stderr,
    read_data,
)

SIMPLE_CASES: List[str] = [
    "attribute_access_on_number_literals",
    "beginning_backslash",
    "bracketmatch",
    "class_blank_parentheses",
    "class_methods_new_line",
    "collections",
    "comments",
    "comments2",
    "comments3",
    "comments4",
    "comments5",
    "comments6",
    "comments_non_breaking_space",
    "comment_after_escaped_newline",
    "composition",
    "composition_no_trailing_comma",
    "docstring",
    "empty_lines",
    "expression",
    "fmtonoff",
    "fmtonoff2",
    "fmtonoff3",
    "fmtonoff4",
    "fmtskip",
    "fmtskip2",
    "fmtskip3",
    "fmtskip4",
    "fmtskip5",
    "fmtskip6",
    "fstring",
    "function",
    "function2",
    "function_trailing_comma",
    "import_spacing",
    "power_op_spacing",
    "remove_parens",
    "slices",
    "string_prefixes",
    "torture",
    "trailing_comma_optional_parens1",
    "trailing_comma_optional_parens2",
    "trailing_comma_optional_parens3",
    "tricky_unicode_symbols",
    "tupleassign",
]

PY310_CASES: List[str] = [
    "pattern_matching_simple",
    "pattern_matching_complex",
    "pattern_matching_extras",
    "pattern_matching_style",
    "pattern_matching_generic",
    "parenthesized_context_managers",
]

PREVIEW_CASES: List[str] = [
    # string processing
    "cantfit",
    "comments7",
    "long_strings",
    "long_strings__edge_case",
    "long_strings__regression",
    "percent_precedence",
]

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
    "src/black_primer/cli.py",
    "src/black_primer/lib.py",
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
    "tests/test_primer.py",
    "tests/optional.py",
    "tests/util.py",
    "tests/conftest.py",
]


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("black.dump_to_file", dump_to_stderr):
        yield


def check_file(filename: str, mode: black.Mode, *, data: bool = True) -> None:
    source, expected = read_data(filename, data=data)
    assert_format(source, expected, mode, fast=False)


@pytest.mark.parametrize("filename", SIMPLE_CASES)
def test_simple_format(filename: str) -> None:
    check_file(filename, DEFAULT_MODE)


@pytest.mark.parametrize("filename", PREVIEW_CASES)
def test_preview_format(filename: str) -> None:
    check_file(filename, black.Mode(preview=True))


@pytest.mark.parametrize("filename", SOURCES)
def test_source_is_formatted(filename: str) -> None:
    path = THIS_DIR.parent / filename
    check_file(str(path), DEFAULT_MODE, data=False)


# =============== #
# Complex cases
# ============= #


def test_empty() -> None:
    source = expected = ""
    assert_format(source, expected)


def test_pep_572() -> None:
    source, expected = read_data("pep_572")
    assert_format(source, expected, minimum_version=(3, 8))


def test_pep_572_remove_parens() -> None:
    source, expected = read_data("pep_572_remove_parens")
    assert_format(source, expected, minimum_version=(3, 8))


def test_pep_572_do_not_remove_parens() -> None:
    source, expected = read_data("pep_572_do_not_remove_parens")
    # the AST safety checks will fail, but that's expected, just make sure no
    # parentheses are touched
    assert_format(source, expected, fast=True)


@pytest.mark.parametrize("major, minor", [(3, 9), (3, 10)])
def test_pep_572_newer_syntax(major: int, minor: int) -> None:
    source, expected = read_data(f"pep_572_py{major}{minor}")
    assert_format(source, expected, minimum_version=(major, minor))


def test_pep_570() -> None:
    source, expected = read_data("pep_570")
    assert_format(source, expected, minimum_version=(3, 8))


@pytest.mark.parametrize("filename", PY310_CASES)
def test_python_310(filename: str) -> None:
    source, expected = read_data(filename)
    mode = black.Mode(target_versions={black.TargetVersion.PY310})
    assert_format(source, expected, mode, minimum_version=(3, 10))


def test_python_310_without_target_version() -> None:
    source, expected = read_data("pattern_matching_simple")
    mode = black.Mode()
    assert_format(source, expected, mode, minimum_version=(3, 10))


def test_patma_invalid() -> None:
    source, expected = read_data("pattern_matching_invalid")
    mode = black.Mode(target_versions={black.TargetVersion.PY310})
    with pytest.raises(black.parsing.InvalidInput) as exc_info:
        assert_format(source, expected, mode, minimum_version=(3, 10))

    exc_info.match("Cannot parse: 10:11")


def test_python_2_hint() -> None:
    with pytest.raises(black.parsing.InvalidInput) as exc_info:
        assert_format("print 'daylily'", "print 'daylily'")
    exc_info.match(black.parsing.PY2_HINT)


def test_docstring_no_string_normalization() -> None:
    """Like test_docstring but with string normalization off."""
    source, expected = read_data("docstring_no_string_normalization")
    mode = replace(DEFAULT_MODE, string_normalization=False)
    assert_format(source, expected, mode)


def test_long_strings_flag_disabled() -> None:
    """Tests for turning off the string processing logic."""
    source, expected = read_data("long_strings_flag_disabled")
    mode = replace(DEFAULT_MODE, experimental_string_processing=False)
    assert_format(source, expected, mode)


def test_numeric_literals() -> None:
    source, expected = read_data("numeric_literals")
    mode = replace(DEFAULT_MODE, target_versions=PY36_VERSIONS)
    assert_format(source, expected, mode)


def test_numeric_literals_ignoring_underscores() -> None:
    source, expected = read_data("numeric_literals_skip_underscores")
    mode = replace(DEFAULT_MODE, target_versions=PY36_VERSIONS)
    assert_format(source, expected, mode)


def test_stub() -> None:
    mode = replace(DEFAULT_MODE, is_pyi=True)
    source, expected = read_data("stub.pyi")
    assert_format(source, expected, mode)


def test_python38() -> None:
    source, expected = read_data("python38")
    assert_format(source, expected, minimum_version=(3, 8))


def test_python39() -> None:
    source, expected = read_data("python39")
    assert_format(source, expected, minimum_version=(3, 9))


def test_power_op_newline() -> None:
    # requires line_length=0
    source, expected = read_data("power_op_newline")
    assert_format(source, expected, mode=black.Mode(line_length=0))
