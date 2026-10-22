# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Export the Python grammar and symbols."""

# Python imports
import os
import re
from collections.abc import Mapping
from io import StringIO
from typing import Union

# Local imports
from .pgen2 import driver, pgen
from .pgen2.grammar import Grammar

# Moved into initialize because mypyc can't handle __file__ (XXX bug)
# # The grammar file
# _GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.txt")
# _PATTERN_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__),
#                                      "PatternGrammar.txt")


class Symbols:
    def __init__(self, grammar: Grammar) -> None:
        """Initializer.

        Creates an attribute for each grammar symbol (nonterminal),
        whose value is the symbol's type (an int >= 256).
        """
        for name, symbol in grammar.symbol2number.items():
            setattr(self, name, symbol)


class _python_symbols(Symbols):
    and_expr: int
    and_test: int
    annassign: int
    arglist: int
    argument: int
    arith_expr: int
    asexpr_test: int
    assert_stmt: int
    async_funcdef: int
    async_stmt: int
    atom: int
    augassign: int
    break_stmt: int
    case_block: int
    classdef: int
    comp_for: int
    comp_if: int
    comp_iter: int
    comp_op: int
    comparison: int
    compound_stmt: int
    continue_stmt: int
    decorated: int
    decorator: int
    decorators: int
    del_stmt: int
    dictsetmaker: int
    dotted_as_name: int
    dotted_as_names: int
    dotted_name: int
    encoding_decl: int
    eval_input: int
    except_clause: int
    expr: int
    expr_stmt: int
    exprlist: int
    factor: int
    file_input: int
    flow_stmt: int
    for_stmt: int
    fstring: int
    fstring_format_spec: int
    fstring_middle: int
    fstring_replacement_field: int
    funcdef: int
    global_stmt: int
    guard: int
    if_stmt: int
    import_as_name: int
    import_as_names: int
    import_from: int
    import_name: int
    import_stmt: int
    lazy_import: int
    lambdef: int
    listmaker: int
    match_stmt: int
    namedexpr_test: int
    not_test: int
    old_comp_for: int
    old_comp_if: int
    old_comp_iter: int
    old_lambdef: int
    old_test: int
    or_test: int
    parameters: int
    paramspec: int
    pass_stmt: int
    pattern: int
    patterns: int
    power: int
    raise_stmt: int
    return_stmt: int
    shift_expr: int
    simple_stmt: int
    single_input: int
    sliceop: int
    small_stmt: int
    subject_expr: int
    star_expr: int
    stmt: int
    subscript: int
    subscriptlist: int
    suite: int
    term: int
    test: int
    testlist: int
    testlist1: int
    testlist_gexp: int
    testlist_safe: int
    testlist_star_expr: int
    tfpdef: int
    tfplist: int
    tname: int
    tname_star: int
    trailer: int
    try_stmt: int
    tstring: int
    tstring_format_spec: int
    tstring_middle: int
    tstring_replacement_field: int
    type_stmt: int
    typedargslist: int
    typeparam: int
    typeparams: int
    typevar: int
    typevartuple: int
    varargslist: int
    vfpdef: int
    vfplist: int
    vname: int
    while_stmt: int
    with_stmt: int
    xor_expr: int
    yield_arg: int
    yield_expr: int
    yield_stmt: int


class _cython_symbols(_python_symbols):
    """The Python symbols, numbered as in the Python grammar, plus Cython's own."""

    cast: int
    cdecl_atom: int
    cdecl_atoms: int
    cdecl_declarator: int
    cdecl_item: int
    cdecl_trailer: int
    cdef_line: int
    cdef_modifiers: int
    cdef_stmt: int
    cdef_suite: int
    cdef_tail: int
    sizeof_expr: int

    def __init__(self, numbers: Mapping[str, int]) -> None:
        for name, symbol in numbers.items():
            setattr(self, name, symbol)


class _pattern_symbols(Symbols):
    Alternative: int
    Alternatives: int
    Details: int
    Matcher: int
    NegatedUnit: int
    Repeater: int
    Unit: int


python_grammar: Grammar
python_grammar_async_keywords: Grammar
python_grammar_soft_keywords: Grammar
pattern_grammar: Grammar
python_symbols: _python_symbols
cython_symbols: _cython_symbols
_cython_numbers: dict[str, int]
pattern_symbols: _pattern_symbols


def _CYTHON_GRAMMAR_FILE() -> str:
    # In a function because mypyc can't handle __file__ at module level.
    return os.path.join(os.path.dirname(__file__), "CythonGrammar.txt")


_cython_grammar: Grammar | None = None


def get_cython_grammar() -> Grammar:
    """Return the grammar for Cython: Python 3.10+ plus the rules of CythonGrammar.txt.

    It is built on first use, as only .pyx, .pxd and .pxi files need it.
    """
    global _cython_grammar
    if _cython_grammar is None:
        with open(
            os.path.join(os.path.dirname(__file__), "Grammar.txt"), encoding="utf-8"
        ) as f:
            text = f.read()
        with open(_CYTHON_GRAMMAR_FILE(), encoding="utf-8") as f:
            text += "\n" + f.read()
        generator = pgen.ParserGenerator("CythonGrammar.txt", StringIO(text))
        order = sorted(_cython_numbers, key=_cython_numbers.__getitem__)
        grammar = generator.make_grammar(order)
        assert grammar.symbol2number == _cython_numbers
        grammar.soft_keywords.clear()
        grammar.soft_keywords.update(python_grammar_soft_keywords.soft_keywords)
        grammar.async_keywords = True
        grammar.version = (3, 10)
        _cython_grammar = grammar
    return _cython_grammar


def initialize(
    cache_dir: Union[str, "os.PathLike[str]", None] = None, *, save: bool = True
) -> None:
    global python_grammar
    global python_grammar_async_keywords
    global python_grammar_soft_keywords
    global python_symbols
    global cython_symbols
    global _cython_numbers
    global pattern_grammar
    global pattern_symbols

    # The grammar file
    _GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.txt")
    _PATTERN_GRAMMAR_FILE = os.path.join(
        os.path.dirname(__file__), "PatternGrammar.txt"
    )

    python_grammar = driver.load_packaged_grammar(_GRAMMAR_FILE, cache_dir, save=save)
    assert "print" not in python_grammar.keywords
    assert "exec" not in python_grammar.keywords

    soft_keywords = python_grammar.soft_keywords.copy()
    python_grammar.soft_keywords.clear()

    python_symbols = _python_symbols(python_grammar)

    # Cython's symbols are numbered after the Python ones so that the two grammars
    # agree on the number of every Python symbol. Work them out from the rule names
    # alone: building the Cython grammar itself is left until it is needed.
    with open(_CYTHON_GRAMMAR_FILE(), encoding="utf-8") as f:
        cython_rules = set(re.findall(r"^(\w+):", f.read(), re.MULTILINE))
    numbers = dict(python_grammar.symbol2number)
    for name in sorted(cython_rules - numbers.keys()):
        numbers[name] = 256 + len(numbers)
    _cython_numbers = numbers
    cython_symbols = _cython_symbols(numbers)

    # Python 3.0-3.6
    python_grammar.version = (3, 0)

    # Python 3.7+
    python_grammar_async_keywords = python_grammar.copy()
    python_grammar_async_keywords.async_keywords = True
    python_grammar_async_keywords.version = (3, 7)

    # Python 3.10+
    python_grammar_soft_keywords = python_grammar_async_keywords.copy()
    python_grammar_soft_keywords.soft_keywords = soft_keywords
    python_grammar_soft_keywords.version = (3, 10)

    pattern_grammar = driver.load_packaged_grammar(
        _PATTERN_GRAMMAR_FILE, cache_dir, save=save
    )
    pattern_symbols = _pattern_symbols(pattern_grammar)
