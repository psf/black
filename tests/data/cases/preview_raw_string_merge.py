# flags: --unstable

plain = (
    r"first "
    r"second"
)
slashes = (
    r"C:\first"
    r"\second"
)
bytes_value = (
    rb"first\n"
    rb"second"
)
quoted = r"a\"b" r"c"
backslashes = r"a\\" r"b"
newlines = r"a\
b" r"c"
unicode_value = r"你好 " r"世界"
# A raw string cannot gain escapes to accommodate the other delimiter.
mixed_quotes = r'contains "double"' r"contains 'single'"
# Mixed prefixes and raw f-strings remain outside the merge contract.
mixed_prefix = r"first\n" "second"
raw_fstring = rf"{value}" rf"second"

# output

plain = r"first second"
slashes = r"C:\first\second"
bytes_value = rb"first\nsecond"
quoted = r"a\"bc"
backslashes = r"a\\b"
newlines = r"a\
bc"
unicode_value = r"你好 世界"
# A raw string cannot gain escapes to accommodate the other delimiter.
mixed_quotes = r'contains "double"' r"contains 'single'"
# Mixed prefixes and raw f-strings remain outside the merge contract.
mixed_prefix = r"first\n" "second"
raw_fstring = rf"{value}" rf"second"
