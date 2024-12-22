# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation.
# All rights reserved.

# mypy: allow-untyped-defs, allow-untyped-calls

"""Tokenization help for Python programs.

generate_tokens(readline) is a generator that breaks a stream of
text into Python tokens.  It accepts a readline-like method which is called
repeatedly to get the next line of input (or "" for EOF).  It generates
5-tuples with these members:

    the token type (see token.py)
    the token (a string)
    the starting (row, column) indices of the token (a 2-tuple of ints)
    the ending (row, column) indices of the token (a 2-tuple of ints)
    the original line (string)

It is designed to match the working of the Python tokenizer exactly, except
that it produces COMMENT tokens for comments and gives type OP for all
operators

Older entry points
    tokenize_loop(readline, tokeneater)
    tokenize(readline, tokeneater=printtoken)
are the same, except instead of generating tokens, tokeneater is a callback
function to which the 5 fields described above are passed as 5 arguments,
each time a new token is found."""

import builtins
import sys
from collections.abc import Callable, Iterable, Iterator
from re import Pattern
from typing import Final, Optional, Union

from blib2to3.pgen2.grammar import Grammar
from blib2to3.pgen2.token import (
    ASYNC,
    AWAIT,
    COMMENT,
    DEDENT,
    ENDMARKER,
    ERRORTOKEN,
    FSTRING_END,
    FSTRING_MIDDLE,
    FSTRING_START,
    INDENT,
    NAME,
    NEWLINE,
    NL,
    NUMBER,
    OP,
    STRING,
    tok_name,
)

__author__ = "Ka-Ping Yee <ping@lfw.org>"
__credits__ = "GvR, ESR, Tim Peters, Thomas Wouters, Fred Drake, Skip Montanaro"

import re
import token
from codecs import BOM_UTF8, lookup

import pytokens
from pytokens import TokenType

from . import token

__all__ = [x for x in dir(token) if x[0] != "_"] + [
    "tokenize",
    "generate_tokens",
    "untokenize",
]
del token

Coord = tuple[int, int]
TokenInfo = tuple[int, str, Coord, Coord, str]

TOKEN_TYPE_MAP = {
    TokenType.indent: INDENT,
    TokenType.dedent: DEDENT,
    TokenType.newline: NEWLINE,
    TokenType.nl: NL,
    TokenType.comment: COMMENT,
    TokenType.semicolon: OP,
    TokenType.lparen: OP,
    TokenType.rparen: OP,
    TokenType.lbracket: OP,
    TokenType.rbracket: OP,
    TokenType.lbrace: OP,
    TokenType.rbrace: OP,
    TokenType.colon: OP,
    TokenType.op: OP,
    TokenType.identifier: NAME,
    TokenType.number: NUMBER,
    TokenType.string: STRING,
    TokenType.fstring_start: FSTRING_START,
    TokenType.fstring_middle: FSTRING_MIDDLE,
    TokenType.fstring_end: FSTRING_END,
    TokenType.endmarker: ENDMARKER

}

class TokenError(Exception): ...

def token_type(token: pytokens.Token, source: str) -> int:
    tok_type = TOKEN_TYPE_MAP[token.type]
    if tok_type == NAME:
        if source == "async":
            return ASYNC

        if source == "await":
            return AWAIT

    return tok_type

def tokenize(source: str, grammar: Grammar | None = None) -> Iterator[TokenInfo]:
    lines = source.split("\n")
    lines += [""]  # For newline tokens in files that don't end in a newline
    line, column = 1, 0
    try:
        for token in pytokens.tokenize(source):
            line, column = token.start_line, token.start_col
            if token.type == TokenType.whitespace:
                continue

            token_string = source[token.start_index:token.end_index]

            if token.type == TokenType.newline and token_string == '':
                # Black doesn't yield empty newline tokens at the end of a file
                # if there's no newline at the end of a file.
                continue

            source_line = lines[token.start_line - 1]

            if token.type == TokenType.op and token_string == "...":
                # Black doesn't have an ellipsis token yet, yield 3 DOTs instead
                assert token.start_line == token.end_line
                assert token.end_col == token.start_col + 3

                token_string = "."
                for start_col in range(token.start_col, token.start_col + 3):
                    end_col = start_col + 1
                    yield (token_type(token, token_string), token_string, (token.start_line, start_col), (token.end_line, end_col), source_line)
            else:
                yield (token_type(token, token_string), token_string, (token.start_line, token.start_col), (token.end_line, token.end_col), source_line)
    except Exception as exc:  # TODO:
        raise TokenError(repr(exc), (line, column))

def printtoken(
    type: int, token: str, srow_col: Coord, erow_col: Coord, line: str
) -> None:  # for testing
    (srow, scol) = srow_col
    (erow, ecol) = erow_col
    print(
        "%d,%d-%d,%d:\t%s\t%s" % (srow, scol, erow, ecol, tok_name[type], repr(token))
    )

if __name__ == "__main__":  # testing
    if len(sys.argv) > 1:
        token_iterator = tokenize(open(sys.argv[1]).read())
    else:
        token_iterator = tokenize(sys.stdin.read())

    for tok in token_iterator:
        printtoken(*tok)
