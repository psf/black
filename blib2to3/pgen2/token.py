"""Token constants (from "token.h")."""

from typing import Dict
from typing_extensions import Final

#  Taken from Python (r53757) and modified to include some tokens
#   originally monkeypatched in by pgen2.tokenize

# --start constants--
ENDMARKER: Final[int] = 0
NAME: Final[int] = 1
NUMBER: Final[int] = 2
STRING: Final[int] = 3
NEWLINE: Final[int] = 4
INDENT: Final[int] = 5
DEDENT: Final[int] = 6
LPAR: Final[int] = 7
RPAR: Final[int] = 8
LSQB: Final[int] = 9
RSQB: Final[int] = 10
COLON: Final[int] = 11
COMMA: Final[int] = 12
SEMI: Final[int] = 13
PLUS: Final[int] = 14
MINUS: Final[int] = 15
STAR: Final[int] = 16
SLASH: Final[int] = 17
VBAR: Final[int] = 18
AMPER: Final[int] = 19
LESS: Final[int] = 20
GREATER: Final[int] = 21
EQUAL: Final[int] = 22
DOT: Final[int] = 23
PERCENT: Final[int] = 24
BACKQUOTE: Final[int] = 25
LBRACE: Final[int] = 26
RBRACE: Final[int] = 27
EQEQUAL: Final[int] = 28
NOTEQUAL: Final[int] = 29
LESSEQUAL: Final[int] = 30
GREATEREQUAL: Final[int] = 31
TILDE: Final[int] = 32
CIRCUMFLEX: Final[int] = 33
LEFTSHIFT: Final[int] = 34
RIGHTSHIFT: Final[int] = 35
DOUBLESTAR: Final[int] = 36
PLUSEQUAL: Final[int] = 37
MINEQUAL: Final[int] = 38
STAREQUAL: Final[int] = 39
SLASHEQUAL: Final[int] = 40
PERCENTEQUAL: Final[int] = 41
AMPEREQUAL: Final[int] = 42
VBAREQUAL: Final[int] = 43
CIRCUMFLEXEQUAL: Final[int] = 44
LEFTSHIFTEQUAL: Final[int] = 45
RIGHTSHIFTEQUAL: Final[int] = 46
DOUBLESTAREQUAL: Final[int] = 47
DOUBLESLASH: Final[int] = 48
DOUBLESLASHEQUAL: Final[int] = 49
AT: Final[int] = 50
ATEQUAL: Final[int] = 51
OP: Final[int] = 52
COMMENT: Final[int] = 53
NL: Final[int] = 54
RARROW: Final[int] = 55
AWAIT: Final[int] = 56
ASYNC: Final[int] = 57
ERRORTOKEN: Final[int] = 58
COLONEQUAL: Final[int] = 59
N_TOKENS: Final[int] = 60
NT_OFFSET: Final[int] = 256
# --end constants--

tok_name: Final[Dict[int, str]] = {}
for _name, _value in list(globals().items()):
    if type(_value) is type(0):
        tok_name[_value] = _name


def ISTERMINAL(x: int) -> bool:
    return x < NT_OFFSET


def ISNONTERMINAL(x: int) -> bool:
    return x >= NT_OFFSET


def ISEOF(x: int) -> bool:
    return x == ENDMARKER
