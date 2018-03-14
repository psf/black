# Stubs for lib2to3.pgen2.grammar (Python 3.6)

from blib2to3.pgen2 import _Path

from typing import Any, Dict, List, Optional, Text, Tuple, TypeVar

_P = TypeVar('_P')
_Label = Tuple[int, Optional[Text]]
_DFA = List[List[Tuple[int, int]]]
_DFAS = Tuple[_DFA, Dict[int, int]]

class Grammar:
    symbol2number: Dict[Text, int]
    number2symbol: Dict[int, Text]
    states: List[_DFA]
    dfas: Dict[int, _DFAS]
    labels: List[_Label]
    keywords: Dict[Text, int]
    tokens: Dict[int, int]
    symbol2label: Dict[Text, int]
    start: int
    def __init__(self) -> None: ...
    def dump(self, filename: _Path) -> None: ...
    def load(self, filename: _Path) -> None: ...
    def copy(self: _P) -> _P: ...
    def report(self) -> None: ...

opmap_raw: Text
opmap: Dict[Text, Text]
