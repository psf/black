from pathlib import Path
from typing import (TYPE_CHECKING, Any, Callable, Collection, Dict, Generator,
                    Generic, Iterable, Iterator, List, Optional, Pattern,
                    Sequence, Set, Sized, Tuple, Type, TypeVar, Union, cast)

from blib2to3.pytree import Leaf, Node

from typing_extensions import Final

if TYPE_CHECKING:
    import colorama  # noqa: F401

# --- Additional Black Types ---
FileContent = str
Encoding = str
NewLine = str
Depth = int
NodeType = int
ParserState = int
LeafID = int
StringID = int
Priority = int
Index = int
LN = Union[Leaf, Node]
Transformer = Callable[["Line", Collection["Feature"]], Iterator["Line"]]
Timestamp = float
FileSize = int
CacheInfo = Tuple[Timestamp, FileSize]
Cache = Dict[Path, CacheInfo]


T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class Ok(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def ok(self) -> T:
        return self._value


class Err(Generic[E]):
    def __init__(self, e: E) -> None:
        self._e = e

    def err(self) -> E:
        return self._e


# The 'Result' return type is used to implement an error-handling model heavily
# influenced by that used by the Rust programming language
# (see https://doc.rust-lang.org/book/ch09-00-error-handling.html).
Result = Union[Ok[T], Err[E]]
