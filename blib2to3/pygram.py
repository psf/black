# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Export the Python grammar and symbols."""

# Python imports
import os

# Local imports
from .pgen2 import token
from .pgen2 import driver
from . import pytree

# The grammar file
_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.txt")
_PATTERN_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__),
                                     "PatternGrammar.txt")


class Symbols(object):

    def __init__(self, grammar):
        """Initializer.

        Creates an attribute for each grammar symbol (nonterminal),
        whose value is the symbol's type (an int >= 256).
        """
        for name, symbol in grammar.symbol2number.items():
            setattr(self, name, symbol)


def initialize(cache_dir=None):
    global python_grammar
    global python_grammar_no_print_statement
    global python_grammar_no_print_statement_no_exec_statement
    global python_symbols
    global pattern_grammar
    global pattern_symbols

    # Python 2
    python_grammar = driver.load_packaged_grammar("blib2to3", _GRAMMAR_FILE,
                                                  cache_dir)

    python_symbols = Symbols(python_grammar)

    # Python 2 + from __future__ import print_function
    python_grammar_no_print_statement = python_grammar.copy()
    del python_grammar_no_print_statement.keywords["print"]

    # Python 3
    python_grammar_no_print_statement_no_exec_statement = python_grammar.copy()
    del python_grammar_no_print_statement_no_exec_statement.keywords["print"]
    del python_grammar_no_print_statement_no_exec_statement.keywords["exec"]

    pattern_grammar = driver.load_packaged_grammar("blib2to3", _PATTERN_GRAMMAR_FILE,
                                                   cache_dir)
    pattern_symbols = Symbols(pattern_grammar)
