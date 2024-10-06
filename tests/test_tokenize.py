"""Tests for the blib2to3 tokenizer."""

import io
import sys
import textwrap
from dataclasses import dataclass
from typing import List

import black
from blib2to3.pgen2 import token, tokenize


@dataclass
class Token:
    type: str
    string: str
    start: tokenize.Coord
    end: tokenize.Coord


def get_tokens(text: str) -> List[Token]:
    """Return the tokens produced by the tokenizer."""
    readline = io.StringIO(text).readline
    tokens: List[Token] = []

    def tokeneater(
        type: int, string: str, start: tokenize.Coord, end: tokenize.Coord, line: str
    ) -> None:
        tokens.append(Token(token.tok_name[type], string, start, end))

    tokenize.tokenize(readline, tokeneater)
    return tokens


def assert_tokenizes(text: str, tokens: List[Token]) -> None:
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
            Token("FSTRING_MIDDLE", "", (1, 2), (1, 2)),
            Token("LBRACE", "{", (1, 2), (1, 3)),
            Token("NAME", "x", (1, 3), (1, 4)),
            Token("RBRACE", "}", (1, 4), (1, 5)),
            Token("FSTRING_MIDDLE", "", (1, 5), (1, 5)),
            Token("FSTRING_END", '"', (1, 5), (1, 6)),
            Token("ENDMARKER", "", (2, 0), (2, 0)),
        ],
    )
    assert_tokenizes(
        'f"{x:y}"\n',
        [
            Token(type="FSTRING_START", string='f"', start=(1, 0), end=(1, 2)),
            Token(type="FSTRING_MIDDLE", string="", start=(1, 2), end=(1, 2)),
            Token(type="LBRACE", string="{", start=(1, 2), end=(1, 3)),
            Token(type="NAME", string="x", start=(1, 3), end=(1, 4)),
            Token(type="OP", string=":", start=(1, 4), end=(1, 5)),
            Token(type="FSTRING_MIDDLE", string="y", start=(1, 5), end=(1, 6)),
            Token(type="RBRACE", string="}", start=(1, 6), end=(1, 7)),
            Token(type="FSTRING_MIDDLE", string="", start=(1, 7), end=(1, 7)),
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
            Token(type="LBRACE", string="{", start=(2, 0), end=(2, 1)),
            Token(type="NAME", string="a", start=(2, 1), end=(2, 2)),
            Token(type="RBRACE", string="}", start=(2, 2), end=(2, 3)),
            Token(type="FSTRING_MIDDLE", string="", start=(2, 3), end=(2, 3)),
            Token(type="FSTRING_END", string='"', start=(2, 3), end=(2, 4)),
            Token(type="NEWLINE", string="\n", start=(2, 4), end=(2, 5)),
            Token(type="ENDMARKER", string="", start=(3, 0), end=(3, 0)),
        ],
    )


# Run "echo some code | python tests/test_tokenize.py" to generate test cases.
if __name__ == "__main__":
    code = sys.stdin.read()
    tokens = get_tokens(code)
    text = f"assert_tokenizes({code!r}, {tokens!r})"
    text = black.format_str(text, mode=black.Mode())
    print(textwrap.indent(text, "    "))
