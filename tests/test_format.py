from unittest.mock import patch

import black
from parameterized import parameterized

from tests.util import (
    BlackBaseTestCase,
    fs,
    ff,
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
    "fstring",
    "function",
    "function2",
    "function_trailing_comma",
    "import_spacing",
    "numeric_literals_py2",
    "python2",
    "python2_unicode_literals",
    "remove_parens",
    "slices",
    "string_prefixes",
    "tricky_unicode_symbols",
    "tupleassign",
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
    "tests/test_black.py",
    "tests/test_format.py",
    "tests/test_blackd.py",
    "src/black/__init__.py",
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
]


class TestSimpleFormat(BlackBaseTestCase):
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
        self.assertFalse(ff(path))

    def check_file(self, filename: str, mode: black.Mode, *, data: bool = True) -> None:
        source, expected = read_data(filename, data=data)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode)
