import unittest
from black.strings import fix_multiline_docstring

class TestFixMultilineDocstring(unittest.TestCase):
    def test_no_unnecessary_newlines(self):
        docstring = '"""This is a docstring.\nIt has multiple lines."""'
        prefix = '    '
        result = fix_multiline_docstring(docstring, prefix)
        self.assertNotIn('\n\n', result)

    def test_line_length_limit(self):
        docstring = '"""This is a short docstring."""'
        prefix = '    '
        result = fix_multiline_docstring(docstring, prefix)
        self.assertEqual(result.count('\n'), 0)

    def test_multiline_docstring(self):
        docstring = '"""This is a multiline docstring.\nIt has multiple lines.\n"""'
        prefix = '    '
        result = fix_multiline_docstring(docstring, prefix)
        self.assertEqual(result.count('\n'), 2)

if __name__ == '__main__':
    unittest.main()
import unittest
from black.strings import fix_multiline_docstring

class TestFixMultilineDocstring(unittest.TestCase):
    def test_no_unnecessary_newlines(self):
        docstring = '"""This is a docstring.\nIt has multiple lines."""'
        prefix = '    '
        result = fix_multiline_docstring(docstring, prefix)
        self.assertNotIn('\n\n', result)

    def test_line_length_limit(self):
        docstring = '"""This is a short docstring."""'
        prefix = '    '
        result = fix_multiline_docstring(docstring, prefix)
        self.assertEqual(result.count('\n'), 0)

    def test_multiline_docstring(self):
        docstring = '"""This is a multiline docstring.\nIt has multiple lines.\n"""'
        prefix = '    '
        result = fix_multiline_docstring(docstring, prefix)
        self.assertEqual(result.count('\n'), 2)

if __name__ == '__main__':
    unittest.main()
