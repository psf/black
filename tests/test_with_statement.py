from black import format_str, FileMode

def test_with_statement_formatting():
    """Test Black's formatting of with statements using tuple arguments."""

    # This is how the user might write the code before Black formats it
    unformatted_code = """\
with (open("file1.txt") as f1, open("file2.txt") as f2):
    pass
"""

    # This is how Black should format it correctly
    expected_code = """\
with open("file1.txt") as f1, open("file2.txt") as f2:
    pass
"""

    # Run Black's formatter
    formatted_code = format_str(unformatted_code, mode=FileMode())

    # Check if Black formats the code correctly
    assert formatted_code == expected_code, "Black did not format with correctly."