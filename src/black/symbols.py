from black.types import *
from blib2to3 import pygram
from blib2to3.pgen2 import token

syms = pygram.python_symbols

WHITESPACE: Final = {token.DEDENT, token.INDENT, token.NEWLINE}
STATEMENT: Final = {
    syms.if_stmt,
    syms.while_stmt,
    syms.for_stmt,
    syms.try_stmt,
    syms.except_clause,
    syms.with_stmt,
    syms.funcdef,
    syms.classdef,
}
STANDALONE_COMMENT: Final = 153
token.tok_name[STANDALONE_COMMENT] = "STANDALONE_COMMENT"
LOGIC_OPERATORS: Final = {"and", "or"}
COMPARATORS: Final = {
    token.LESS,
    token.GREATER,
    token.EQEQUAL,
    token.NOTEQUAL,
    token.LESSEQUAL,
    token.GREATEREQUAL,
}
MATH_OPERATORS: Final = {
    token.VBAR,
    token.CIRCUMFLEX,
    token.AMPER,
    token.LEFTSHIFT,
    token.RIGHTSHIFT,
    token.PLUS,
    token.MINUS,
    token.STAR,
    token.SLASH,
    token.DOUBLESLASH,
    token.PERCENT,
    token.AT,
    token.TILDE,
    token.DOUBLESTAR,
}
STARS: Final = {token.STAR, token.DOUBLESTAR}
VARARGS_SPECIALS: Final = STARS | {token.SLASH}
VARARGS_PARENTS: Final = {
    syms.arglist,
    syms.argument,  # double star in arglist
    syms.trailer,  # single argument to call
    syms.typedargslist,
    syms.varargslist,  # lambdas
}
UNPACKING_PARENTS: Final = {
    syms.atom,  # single element of a list or set literal
    syms.dictsetmaker,
    syms.listmaker,
    syms.testlist_gexp,
    syms.testlist_star_expr,
}
TEST_DESCENDANTS: Final = {
    syms.test,
    syms.lambdef,
    syms.or_test,
    syms.and_test,
    syms.not_test,
    syms.comparison,
    syms.star_expr,
    syms.expr,
    syms.xor_expr,
    syms.and_expr,
    syms.shift_expr,
    syms.arith_expr,
    syms.trailer,
    syms.term,
    syms.power,
}
ASSIGNMENTS: Final = {
    "=",
    "+=",
    "-=",
    "*=",
    "@=",
    "/=",
    "%=",
    "&=",
    "|=",
    "^=",
    "<<=",
    ">>=",
    "**=",
    "//=",
}


IMPLICIT_TUPLE = {syms.testlist, syms.testlist_star_expr, syms.exprlist}
BRACKET = {token.LPAR: token.RPAR, token.LSQB: token.RSQB, token.LBRACE: token.RBRACE}
OPENING_BRACKETS = set(BRACKET.keys())
CLOSING_BRACKETS = set(BRACKET.values())
BRACKETS = OPENING_BRACKETS | CLOSING_BRACKETS
ALWAYS_NO_SPACE = CLOSING_BRACKETS | {token.COMMA, STANDALONE_COMMENT}

FMT_OFF = {"# fmt: off", "# fmt:off", "# yapf: disable"}
FMT_ON = {"# fmt: on", "# fmt:on", "# yapf: enable"}


STRING_PREFIX_CHARS: Final = "furbFURB"  # All possible string prefix characters.
