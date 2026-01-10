"""Tests for the blib2to3 tokenizer."""

import sys
import textwrap
from dataclasses import dataclass

import black
from blib2to3.pgen2 import token, tokenize


@dataclass
class Token:
    type: str
    string: str
    start: tokenize.Coord
    end: tokenize.Coord


def get_tokens(text: str) -> list[Token]:
    """Return the tokens produced by the tokenizer."""
    return [
        Token(token.tok_name[tok_type], string, start, end)
        for tok_type, string, start, end, _ in tokenize.tokenize(text)
    ]


def assert_tokenizes(text: str, tokens: list[Token]) -> None:
    """Assert that the tokenizer produces the expected tokens."""
    actual_tokens = get_tokens(text)
    assert actual_tokens == tokens


def test_simple() -> None:
    assert_tokenizes(
        "1",
        [Token("NUMBER", "1", (1, 0), (1, 1)), Token("ENDMARKER", "", (2, 0), (2, 0))],
    )
    assert_tokenizes(
        "'a'",
        [
            Token("STRING", "'a'", (1, 0), (1, 3)),
            Token("ENDMARKER", "", (2, 0), (2, 0)),
        ],
    )
    assert_tokenizes(
        "a",
        [Token("NAME", "a", (1, 0), (1, 1)), Token("ENDMARKER", "", (2, 0), (2, 0))],
    )


def test_fstring() -> None:
    assert_tokenizes(
        'f"x"',
        [
            Token("FSTRING_START", 'f"', (1, 0), (1, 2)),
            Token("FSTRING_MIDDLE", "x", (1, 2), (1, 3)),
            Token("FSTRING_END", '"', (1, 3), (1, 4)),
            Token("ENDMARKER", "", (2, 0), (2, 0)),
        ],
    )
    assert_tokenizes(
        'f"{x}"',
        [
            Token("FSTRING_START", 'f"', (1, 0), (1, 2)),
            Token("OP", "{", (1, 2), (1, 3)),
            Token("NAME", "x", (1, 3), (1, 4)),
            Token("OP", "}", (1, 4), (1, 5)),
            Token("FSTRING_END", '"', (1, 5), (1, 6)),
            Token("ENDMARKER", "", (2, 0), (2, 0)),
        ],
    )
    assert_tokenizes(
        'f"{x:y}"\n',
        [
            Token(type="FSTRING_START", string='f"', start=(1, 0), end=(1, 2)),
            Token(type="OP", string="{", start=(1, 2), end=(1, 3)),
            Token(type="NAME", string="x", start=(1, 3), end=(1, 4)),
            Token(type="OP", string=":", start=(1, 4), end=(1, 5)),
            Token(type="FSTRING_MIDDLE", string="y", start=(1, 5), end=(1, 6)),
            Token(type="OP", string="}", start=(1, 6), end=(1, 7)),
            Token(type="FSTRING_END", string='"', start=(1, 7), end=(1, 8)),
            Token(type="NEWLINE", string="\n", start=(1, 8), end=(1, 9)),
            Token(type="ENDMARKER", string="", start=(2, 0), end=(2, 0)),
        ],
    )
    assert_tokenizes(
        'f"x\\\n{a}"\n',
        [
            Token(type="FSTRING_START", string='f"', start=(1, 0), end=(1, 2)),
            Token(type="FSTRING_MIDDLE", string="x\\\n", start=(1, 2), end=(2, 0)),
            Token(type="OP", string="{", start=(2, 0), end=(2, 1)),
            Token(type="NAME", string="a", start=(2, 1), end=(2, 2)),
            Token(type="OP", string="}", start=(2, 2), end=(2, 3)),
            Token(type="FSTRING_END", string='"', start=(2, 3), end=(2, 4)),
            Token(type="NEWLINE", string="\n", start=(2, 4), end=(2, 5)),
            Token(type="ENDMARKER", string="", start=(3, 0), end=(3, 0)),
        ],
    )


def test_backslash_continuation() -> None:
    """Test that backslash continuations with no indentation are handled correctly.
    
    This is a regression test for https://github.com/psf/black/issues/XXXX
    where Black failed to parse code with backslash continuations followed by
    unindented lines.
    """
    # Simple case: backslash continuation with unindented number
    assert_tokenizes(
        "if True:\n    foo = 1+\\\n2\n    print(foo)\n",
        [
            Token(type="NAME", string="if", start=(1, 0), end=(1, 2)),
            Token(type="NAME", string="True", start=(1, 3), end=(1, 7)),
            Token(type="OP", string=":", start=(1, 7), end=(1, 8)),
            Token(type="NEWLINE", string="\n", start=(1, 8), end=(1, 9)),
            Token(type="INDENT", string="    ", start=(2, 0), end=(2, 4)),
            Token(type="NAME", string="foo", start=(2, 4), end=(2, 7)),
            Token(type="OP", string="=", start=(2, 8), end=(2, 9)),
            Token(type="NUMBER", string="1", start=(2, 10), end=(2, 11)),
            Token(type="OP", string="+", start=(2, 11), end=(2, 12)),
            Token(type="NL", string="\\\n", start=(2, 12), end=(2, 14)),
            Token(type="NUMBER", string="2", start=(3, 0), end=(3, 1)),
            Token(type="NEWLINE", string="\n", start=(3, 1), end=(3, 2)),
            Token(type="NAME", string="print", start=(4, 4), end=(4, 9)),
            Token(type="OP", string="(", start=(4, 9), end=(4, 10)),
            Token(type="NAME", string="foo", start=(4, 10), end=(4, 13)),
            Token(type="OP", string=")", start=(4, 13), end=(4, 14)),
            Token(type="NEWLINE", string="\n", start=(4, 14), end=(4, 15)),
            Token(type="DEDENT", string="", start=(5, 0), end=(5, 0)),
            Token(type="ENDMARKER", string="", start=(5, 0), end=(5, 0)),
        ],
    )
    
    # Multiple backslash continuations
    assert_tokenizes(
        "if True:\n    result = 1+\\\n2+\\\n3\n    print(result)\n",
        [
            Token(type="NAME", string="if", start=(1, 0), end=(1, 2)),
            Token(type="NAME", string="True", start=(1, 3), end=(1, 7)),
            Token(type="OP", string=":", start=(1, 7), end=(1, 8)),
            Token(type="NEWLINE", string="\n", start=(1, 8), end=(1, 9)),
            Token(type="INDENT", string="    ", start=(2, 0), end=(2, 4)),
            Token(type="NAME", string="result", start=(2, 4), end=(2, 10)),
            Token(type="OP", string="=", start=(2, 11), end=(2, 12)),
            Token(type="NUMBER", string="1", start=(2, 13), end=(2, 14)),
            Token(type="OP", string="+", start=(2, 14), end=(2, 15)),
            Token(type="NL", string="\\\n", start=(2, 15), end=(2, 17)),
            Token(type="NUMBER", string="2", start=(3, 0), end=(3, 1)),
            Token(type="OP", string="+", start=(3, 1), end=(3, 2)),
            Token(type="NL", string="\\\n", start=(3, 2), end=(3, 4)),
            Token(type="NUMBER", string="3", start=(4, 0), end=(4, 1)),
            Token(type="NEWLINE", string="\n", start=(4, 1), end=(4, 2)),
            Token(type="NAME", string="print", start=(5, 4), end=(5, 9)),
            Token(type="OP", string="(", start=(5, 9), end=(5, 10)),
            Token(type="NAME", string="result", start=(5, 10), end=(5, 16)),
            Token(type="OP", string=")", start=(5, 16), end=(5, 17)),
            Token(type="NEWLINE", string="\n", start=(5, 17), end=(5, 18)),
            Token(type="DEDENT", string="", start=(6, 0), end=(6, 0)),
            Token(type="ENDMARKER", string="", start=(6, 0), end=(6, 0)),
        ],
    )


# Run "echo some code | python tests/test_tokenize.py" to generate test cases.
if __name__ == "__main__":
    code = sys.stdin.read()
    tokens = get_tokens(code)
    text = f"assert_tokenizes({code!r}, {tokens!r})"
    text = black.format_str(text, mode=black.Mode())
    print(textwrap.indent(text, "    "))
