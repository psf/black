"""
String-related utility functions.
"""

import regex as re
import sys
import tempfile
from typing import List, Pattern

from mypy_extensions import mypyc_attr

from black.const import STRING_PREFIX_CHARS


def sub_twice(regex: Pattern[str], replacement: str, original: str) -> str:
    """Replace `regex` with `replacement` twice on `original`.

    This is used by string normalization to perform replaces on
    overlapping matches.
    """
    return regex.sub(replacement, regex.sub(replacement, original))


def format_hex(text: str) -> str:
    """
    Formats a hexadecimal string like "0x12B3"
    """
    before, after = text[:2], text[2:]
    return f"{before}{after.upper()}"


def format_scientific_notation(text: str) -> str:
    """Formats a numeric string utilizing scentific notation"""
    before, after = text.split("e")
    sign = ""
    if after.startswith("-"):
        after = after[1:]
        sign = "-"
    elif after.startswith("+"):
        after = after[1:]
    before = format_float_or_int_string(before)
    return f"{before}e{sign}{after}"


def format_long_or_complex_number(text: str) -> str:
    """Formats a long or complex string like `10L` or `10j`"""
    number = text[:-1]
    suffix = text[-1]
    # Capitalize in "2L" because "l" looks too similar to "1".
    if suffix == "l":
        suffix = "L"
    return f"{format_float_or_int_string(number)}{suffix}"


def format_float_or_int_string(text: str) -> str:
    """Formats a float string like "1.0"."""
    if "." not in text:
        return text

    before, after = text.split(".")
    return f"{before or 0}.{after or 0}"


def re_compile_maybe_verbose(regex: str) -> Pattern[str]:
    """Compile a regular expression string in `regex`.

    If it contains newlines, use verbose mode.
    """
    if "\n" in regex:
        regex = "(?x)" + regex
    compiled: Pattern[str] = re.compile(regex)
    return compiled


def has_triple_quotes(string: str) -> bool:
    """
    Returns:
        True iff @string starts with three quotation characters.
    """
    raw_string = string.lstrip(STRING_PREFIX_CHARS)
    return raw_string[:3] in {'"""', "'''"}


@mypyc_attr(patchable=True)
def dump_to_file(*output: str, ensure_final_newline: bool = True) -> str:
    """Dump `output` to a temporary file. Return path to the file."""
    with tempfile.NamedTemporaryFile(
        mode="w", prefix="blk_", suffix=".log", delete=False, encoding="utf8"
    ) as f:
        for lines in output:
            f.write(lines)
            if ensure_final_newline and lines and lines[-1] != "\n":
                f.write("\n")
    return f.name


def lines_with_leading_tabs_expanded(s: str) -> List[str]:
    """
    Splits string into lines and expands only leading tabs (following the normal
    Python rules)
    """
    lines = []
    for line in s.splitlines():
        # Find the index of the first non-whitespace character after a string of
        # whitespace that includes at least one tab
        match = re.match(r"\s*\t+\s*(\S)", line)
        if match:
            first_non_whitespace_idx = match.start(1)

            lines.append(
                line[:first_non_whitespace_idx].expandtabs()
                + line[first_non_whitespace_idx:]
            )
        else:
            lines.append(line)
    return lines


def fix_docstring(docstring: str, prefix: str) -> str:
    # https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    if not docstring:
        return ""
    lines = lines_with_leading_tabs_expanded(docstring)
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        last_line_idx = len(lines) - 2
        for i, line in enumerate(lines[1:]):
            stripped_line = line[indent:].rstrip()
            if stripped_line or i == last_line_idx:
                trimmed.append(prefix + stripped_line)
            else:
                trimmed.append("")
    return "\n".join(trimmed)


def diff(a: str, b: str, a_name: str, b_name: str) -> str:
    """Return a unified diff string between strings `a` and `b`."""
    import difflib

    a_lines = [line for line in a.splitlines(keepends=True)]
    b_lines = [line for line in b.splitlines(keepends=True)]
    diff_lines = []
    for line in difflib.unified_diff(
        a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5
    ):
        # Work around https://bugs.python.org/issue2142
        # See https://www.gnu.org/software/diffutils/manual/html_node/Incomplete-Lines.html
        if line[-1] == "\n":
            diff_lines.append(line)
        else:
            diff_lines.append(line + "\n")
            diff_lines.append("\\ No newline at end of file\n")
    return "".join(diff_lines)


def color_diff(contents: str) -> str:
    """Inject the ANSI color codes to the diff."""
    lines = contents.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("+++") or line.startswith("---"):
            line = "\033[1;37m" + line + "\033[0m"  # bold white, reset
        elif line.startswith("@@"):
            line = "\033[36m" + line + "\033[0m"  # cyan, reset
        elif line.startswith("+"):
            line = "\033[32m" + line + "\033[0m"  # green, reset
        elif line.startswith("-"):
            line = "\033[31m" + line + "\033[0m"  # red, reset
        lines[i] = line
    return "\n".join(lines)


def get_string_prefix(string: str) -> str:
    """
    Pre-conditions:
        * assert_is_leaf_string(@string)

    Returns:
        @string's prefix (e.g. '', 'r', 'f', or 'rf').
    """
    assert_is_leaf_string(string)

    prefix = ""
    prefix_idx = 0
    while string[prefix_idx] in STRING_PREFIX_CHARS:
        prefix += string[prefix_idx].lower()
        prefix_idx += 1

    return prefix


def assert_is_leaf_string(string: str) -> None:
    """
    Checks the pre-condition that @string has the format that you would expect
    of `leaf.value` where `leaf` is some Leaf such that `leaf.type ==
    token.STRING`. A more precise description of the pre-conditions that are
    checked are listed below.

    Pre-conditions:
        * @string starts with either ', ", <prefix>', or <prefix>" where
        `set(<prefix>)` is some subset of `set(STRING_PREFIX_CHARS)`.
        * @string ends with a quote character (' or ").

    Raises:
        AssertionError(...) if the pre-conditions listed above are not
        satisfied.
    """
    dquote_idx = string.find('"')
    squote_idx = string.find("'")
    if -1 in [dquote_idx, squote_idx]:
        quote_idx = max(dquote_idx, squote_idx)
    else:
        quote_idx = min(squote_idx, dquote_idx)

    assert (
        0 <= quote_idx < len(string) - 1
    ), f"{string!r} is missing a starting quote character (' or \")."
    assert string[-1] in (
        "'",
        '"',
    ), f"{string!r} is missing an ending quote character (' or \")."
    assert set(string[:quote_idx]).issubset(
        set(STRING_PREFIX_CHARS)
    ), f"{set(string[:quote_idx])} is NOT a subset of {set(STRING_PREFIX_CHARS)}."
