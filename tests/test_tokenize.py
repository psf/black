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


def test_lazy_import_after_semicolon_and_colon() -> None:
    assert (
        [t.type for t in get_tokens("x = 1; lazy import os\n") if t.string == "lazy"]
        == ["LAZY"]
    )
    assert (
        black.format_str("x = 1; lazy import os\n", mode=black.Mode())
        == "x = 1\nlazy import os\n"
    )

    assert [
        t.type
        for t in get_tokens("lazy import a; lazy from b import c\n")
        if t.string == "lazy"
    ] == ["LAZY", "LAZY"]
    assert (
        black.format_str("lazy import a; lazy from b import c\n", mode=black.Mode())
        == "lazy import a\nlazy from b import c\n"
    )

    assert (
        [t.type for t in get_tokens("if True: lazy import os\n") if t.string == "lazy"]
        == ["LAZY"]
    )
    assert (
        black.format_str("if True: lazy import os\n", mode=black.Mode())
        == "if True:\n    lazy import os\n"
    )

    assert [
        t.type
        for t in get_tokens("try: lazy from os import path\nexcept Exception: pass\n")
        if t.string == "lazy"
    ] == ["LAZY"]
    assert (
        black.format_str(
            "try: lazy from os import path\nexcept Exception: pass\n",
            mode=black.Mode(),
        )
        == "try:\n    lazy from os import path\nexcept Exception:\n    pass\n"
    )

    # Non-import uses of `lazy` after `:` must remain ordinary identifiers.
    for src in (
        "d = {1: lazy}\n",
        "def f(x: lazy = 1): pass\n",
        "x = a[1:lazy]\n",
        "x: lazy\nimport os\n",
    ):
        assert [t.type for t in get_tokens(src) if t.string == "lazy"] == ["NAME"]


def test_lazy_import_with_backslash_continuation() -> None:
    assert_tokenizes(
        "lazy \\\nimport os\n",
        [
            Token("LAZY", "lazy", (1, 0), (1, 4)),
            Token("NL", "\\\n", (1, 5), (1, 7)),
            Token("NAME", "import", (2, 0), (2, 6)),
            Token("NAME", "os", (2, 7), (2, 9)),
            Token("NEWLINE", "\n", (2, 9), (2, 10)),
            Token("ENDMARKER", "", (3, 0), (3, 0)),
        ],
    )
    assert (
        black.format_str("lazy \\\nimport os\n", mode=black.Mode())
        == "lazy import os\n"
    )
    assert (
        black.format_str("lazy \\\nfrom os import path\n", mode=black.Mode())
        == "lazy from os import path\n"
    )
    assert (
        black.format_str("lazy \\\n\\\nfrom os import path\n", mode=black.Mode())
        == "lazy from os import path\n"
    )
    assert (
        black.format_str("if True: lazy \\\nimport os\n", mode=black.Mode())
        == "if True:\n    lazy import os\n"
    )

    # Non-import uses with backslash continuation or newlines remain NAME.
    assert_tokenizes(
        "lazy \\\n= 1\n",
        [
            Token("NAME", "lazy", (1, 0), (1, 4)),
            Token("NL", "\\\n", (1, 5), (1, 7)),
            Token("OP", "=", (2, 0), (2, 1)),
            Token("NUMBER", "1", (2, 2), (2, 3)),
            Token("NEWLINE", "\n", (2, 3), (2, 4)),
            Token("ENDMARKER", "", (3, 0), (3, 0)),
        ],
    )
    assert black.format_str("lazy \\\n= 1\n", mode=black.Mode()) == "lazy = 1\n"
    assert (
        [t.type for t in get_tokens("lazy\nimport os\n") if t.string == "lazy"]
        == ["NAME"]
    )
    assert [
        t.type for t in get_tokens("lazy  # comment\nimport os\n") if t.string == "lazy"
    ] == ["NAME"]


# Run "echo some code | python tests/test_tokenize.py" to generate test cases.
if __name__ == "__main__":
    code = sys.stdin.read()
    tokens = get_tokens(code)
    text = f"assert_tokenizes({code!r}, {tokens!r})"
    text = black.format_str(text, mode=black.Mode())
    print(textwrap.indent(text, "    "))
