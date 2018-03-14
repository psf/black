# Stubs for lib2to3.pgen2.driver (Python 3.6)

import os
import sys
from typing import Any, Callable, IO, Iterable, List, Optional, Text, Tuple, Union

from logging import Logger
from blib2to3.pytree import _Convert, _NL
from blib2to3.pgen2 import _Path
from blib2to3.pgen2.grammar import Grammar


class Driver:
    grammar: Grammar
    logger: Logger
    convert: _Convert
    def __init__(self, grammar: Grammar, convert: Optional[_Convert] = ..., logger: Optional[Logger] = ...) -> None: ...
    def parse_tokens(self, tokens: Iterable[Any], debug: bool = ...) -> _NL: ...
    def parse_stream_raw(self, stream: IO[Text], debug: bool = ...) -> _NL: ...
    def parse_stream(self, stream: IO[Text], debug: bool = ...) -> _NL: ...
    def parse_file(self, filename: _Path, encoding: Optional[Text] = ..., debug: bool = ...) -> _NL: ...
    def parse_string(self, text: Text, debug: bool = ...) -> _NL: ...

def load_grammar(gt: Text = ..., gp: Optional[Text] = ..., save: bool = ..., force: bool = ..., logger: Optional[Logger] = ...) -> Grammar: ...
