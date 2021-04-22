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
    "cantfit",
    "class_blank_parentheses",
    "class_methods_new_line",
    "collections",
    "comments",
    "comments2",
    "comments3",
    "comments4",
    "comments5",
    "comments6",
    "comments7",
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
    "long_strings",
    "long_strings__edge_case",
    "long_strings__regression",
    "numeric_literals_py2",
    "percent_precedence",
    "python2",
    "python2_unicode_literals",
    "remove_parens",
    "slices",
    "string_prefixes",
    "tricky_unicode_symbols",
    "tupleassign",
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
        source, expected = read_data(filename)
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)

    @parameterized.expand(SOURCES)
    @patch("black.dump_to_file", dump_to_stderr)
    def test_source_is_formatted(self, filename: str) -> None:
        path = THIS_DIR.parent / filename
        source, expected = read_data(str(path), data=False)
        actual = fs(source, mode=DEFAULT_MODE)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)
        self.assertFalse(ff(path))
