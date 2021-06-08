from unittest.mock import patch

import black
import pytest
from parameterized import parameterized

from tests.util import (
    BlackBaseTestCase,
    fs,
    DEFAULT_MODE,
    dump_to_stderr,
    read_data,
    THIS_DIR,
)

SIMPLE_CASES = [
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
    "remove_parens",
    "slices",
    "string_prefixes",
    "tricky_unicode_symbols",
    "tupleassign",
]

SIMPLE_CASES_PY2 = [
    "numeric_literals_py2",
    "python2",
    "python2_unicode_literals",
]

EXPERIMENTAL_STRING_PROCESSING_CASES = [
    "cantfit",
    "comments7",
    "long_strings",
    "long_strings__edge_case",
    "long_strings__regression",
    "percent_precedence",
]


SOURCES = [
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
    "tests/test_primer.py",
    "tests/optional.py",
    "tests/util.py",
    "tests/conftest.py",
]


class TestSimpleFormat(BlackBaseTestCase):
    @parameterized.expand(SIMPLE_CASES_PY2)
    @pytest.mark.python2
    @patch("black.dump_to_file", dump_to_stderr)
    def test_simple_format_py2(self, filename: str) -> None:
        self.check_file(filename, DEFAULT_MODE)

    @parameterized.expand(SIMPLE_CASES)
    @patch("black.dump_to_file", dump_to_stderr)
    def test_simple_format(self, filename: str) -> None:
        self.check_file(filename, DEFAULT_MODE)

    @parameterized.expand(EXPERIMENTAL_STRING_PROCESSING_CASES)
    @patch("black.dump_to_file", dump_to_stderr)
    def test_experimental_format(self, filename: str) -> None:
        self.check_file(filename, black.Mode(experimental_string_processing=True))

    @parameterized.expand(SOURCES)
    @patch("black.dump_to_file", dump_to_stderr)
    def test_source_is_formatted(self, filename: str) -> None:
        path = THIS_DIR.parent / filename
        self.check_file(str(path), DEFAULT_MODE, data=False)

    def check_file(self, filename: str, mode: black.Mode, *, data: bool = True) -> None:
        source, expected = read_data(filename, data=data)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        if source != actual:
            black.assert_equivalent(source, actual)
            black.assert_stable(source, actual, mode)
