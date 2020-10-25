from unittest.mock import patch

import black
from parameterized import parameterized

from tests.util import BlackBaseTestCase, read_data, fs, DEFAULT_MODE, dump_to_stderr

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


class TestSimpleFormat(BlackBaseTestCase):
    @parameterized.expand(SIMPLE_CASES)
    @patch("black.dump_to_file", dump_to_stderr)
    def test_simple_format(self, filename):
        source, expected = read_data(filename)
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)
