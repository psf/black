# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""
Python parse tree definitions.

This is a very concrete parse tree; we need to keep every token and
even the comments and whitespace between tokens.

There's also a pattern matching implementation here.
"""

# mypy: allow-untyped-defs, allow-incomplete-defs

from collections.abc import Iterator
from typing import Any, Optional, TypeVar, Union

from blib2to3.pgen2.grammar import Grammar

__author__ = "Guido van Rossum <guido@python.org>"


_type_reprs: dict[int, str | int] = {}


def type_repr(type_num: int) -> str | int:
    global _type_reprs
    if not _type_reprs:
        from . import pygram

        if not hasattr(pygram, "python_symbols"):
            pygram.initialize(cache_dir=None)

        # printing tokens is possible but not as useful
        # from .pgen2 import token // token.__dict__.items():
        for name in dir(pygram.python_symbols):
            val = getattr(pygram.python_symbols, name)
            if type(val) == int:
                _type_reprs[val] = name
    return _type_reprs.setdefault(type_num, type_num)


_P = TypeVar("_P", bound="Base")

NL = Union["Node", "Leaf"]
Context = tuple[str, tuple[int, int]]
RawNode = tuple[int, Optional[str], Optional[Context], Optional[list[NL]]]


class Base:
    """
    Abstract base class for Node and Leaf.

    This provides some default functionality and boilerplate using the
    template pattern.

    A node may be a subnode of at most one parent.
    """

    # Default values for instance variables
    type: int  # int: token number (< 256) or symbol number (>= 256)
    parent: Optional["Node"] = None  # Parent node pointer, or None
    children: list[NL]  # List of subnodes

    def __new__(cls, *args, **kwds):
        """Constructor that prevents Base from being instantiated."""
        assert cls is not Base, "Cannot instantiate Base"
        return object.__new__(cls)

    def __eq__(self, other: Any) -> bool:
        """
        Compare two nodes for equality.

        This calls the method _eq().
        """
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self._eq(other)

    @property
    def prefix(self) -> str:
        raise NotImplementedError

    def _eq(self: _P, other: _P) -> bool:
        """
        Compare two nodes for equality.

        This is called by __eq__ and __ne__.  It is only called if the two nodes
        have the same type.  This must be implemented by the concrete subclass.
        Nodes should be considered equal if they have the same structure,
        ignoring the prefix string and other context information.
        """
        raise NotImplementedError

    def __deepcopy__(self: _P) -> _P:
        return self.clone()

    def clone(self: _P) -> _P:
        """
        Return a cloned (deep) copy of self.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    def pre_order(self) -> Iterator[NL]:
        """
        Return a pre-order iterator for the tree.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    def replace(self, new: NL | list[NL]) -> None:
        """Replace this node with a new one in the parent."""
        assert self.parent is not None, str(self)
        assert new is not None
        if not isinstance(new, list):
            new = [new]
        parent = self.parent
        for i, ch in enumerate(parent.children):
            if ch is self:
                break
        else:
            raise AssertionError((parent.children, self, new))
        # Splice the new children in place of `self` and keep the cached sibling
        # maps valid without rebuilding them, which would be O(len(children)) per
        # call and quadratic when many children are replaced while siblings are
        # read in between (e.g. merging implicitly concatenated strings).
        parent._replace_child_in_sibling_maps(self, new)
        parent.children[i : i + 1] = new
        for x in new:
            x.parent = parent
        self.parent = None

    def get_lineno(self) -> int | None:
        """Return the line number which generated the invocant node."""
        node = self
        while not isinstance(node, Leaf):
            if not node.children:
                return None
            node = node.children[0]
        return node.lineno

    def remove(self, search_start: int = 0) -> int | None:
        """
        Remove the node from the tree. Returns the position of the node in its
        parent's children before it was removed.

        ``search_start`` hints where to begin looking in the parent's children.
        A caller that removes many siblings of the same parent in left-to-right
        order can pass the last returned position to avoid rescanning the whole
        list from index 0 every time, which is quadratic over the parent. The
        entire list is still searched (starting at the hint and wrapping around),
        so an inaccurate hint only costs a little extra scanning.
        """
        if self.parent:
            children = self.parent.children
            count = len(children)
            for offset in range(count):
                i = (search_start + offset) % count
                if children[i] is self:
                    del children[i]
                    self.parent._remove_from_sibling_maps(self)
                    self.parent = None
                    return i
        return None

    @property
    def next_sibling(self) -> NL | None:
        """
        The node immediately following the invocant in their parent's children
        list. If the invocant does not have a next sibling, it is None
        """
        if self.parent is None:
            return None

        if self.parent.next_sibling_map is None:
            self.parent.update_sibling_maps()
        assert self.parent.next_sibling_map is not None
        return self.parent.next_sibling_map[id(self)]

    @property
    def prev_sibling(self) -> NL | None:
        """
        The node immediately preceding the invocant in their parent's children
        list. If the invocant does not have a previous sibling, it is None.
        """
        if self.parent is None:
            return None

        if self.parent.prev_sibling_map is None:
            self.parent.update_sibling_maps()
        assert self.parent.prev_sibling_map is not None
        return self.parent.prev_sibling_map[id(self)]

    def leaves(self) -> Iterator["Leaf"]:
        # Walk iteratively rather than recursing with `yield from`, whose per-node
        # generator delegation is O(depth) and makes a full traversal quadratic on
        # deeply nested trees (e.g. a long `a ** b ** c ** ...` chain).
        stack: list[NL] = list(reversed(self.children))
        while stack:
            node = stack.pop()
            if isinstance(node, Leaf):
                yield node
            else:
                stack.extend(reversed(node.children))

    def depth(self) -> int:
        if self.parent is None:
            return 0
        return 1 + self.parent.depth()


class Node(Base):
    """Concrete implementation for interior nodes."""

    def __init__(
        self,
        type: int,
        children: list[NL],
        prefix: str | None = None,
    ) -> None:
        """
        Initializer.

        Takes a type constant (a symbol number >= 256), a sequence of
        child nodes, and an optional prefix argument.

        As a side effect, the parent pointers of the children are updated.
        """
        assert type >= 256, type
        self.type = type
        self.children = list(children)
        for ch in self.children:
            assert ch.parent is None, repr(ch)
            ch.parent = self
        self.invalidate_sibling_maps()
        if prefix is not None:
            self.prefix = prefix

    def __repr__(self) -> str:
        """Return a canonical string representation."""
        assert self.type is not None
        return f"{self.__class__.__name__}({type_repr(self.type)}, {self.children!r})"

    def __str__(self) -> str:
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        return "".join(map(str, self.children))

    def _eq(self, other: Base) -> bool:
        """Compare two nodes for equality."""
        return (self.type, self.children) == (other.type, other.children)

    def clone(self) -> "Node":
        assert self.type is not None
        """Return a cloned (deep) copy of self."""
        return Node(
            self.type,
            [ch.clone() for ch in self.children],
            self.prefix,
        )

    def pre_order(self) -> Iterator[NL]:
        """Return a pre-order iterator for the tree."""
        # Walk iteratively rather than recursing with `yield from`. The recursive
        # form resumes one delegating generator per level on every step, so a full
        # traversal costs O(depth) per node and is quadratic on deeply nested trees.
        stack: list[NL] = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    @property
    def prefix(self) -> str:
        """
        The whitespace and comments preceding this node in the input.
        """
        if not self.children:
            return ""
        return self.children[0].prefix

    @prefix.setter
    def prefix(self, prefix: str) -> None:
        if self.children:
            self.children[0].prefix = prefix

    def set_child(self, i: int, child: NL) -> None:
        """
        Equivalent to 'node.children[i] = child'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        old = self.children[i]
        old.parent = None
        self.children[i] = child
        self._replace_in_sibling_maps(old, child)

    def insert_child(self, i: int, child: NL) -> None:
        """
        Equivalent to 'node.children.insert(i, child)'. This method also sets
        the child's parent attribute appropriately.
        """
        child.parent = self
        self.children.insert(i, child)
        if 0 <= i < len(self.children) and self.children[i] is child:
            self._insert_into_sibling_maps(i, child)
        else:
            self.invalidate_sibling_maps()

    def append_child(self, child: NL) -> None:
        """
        Equivalent to 'node.children.append(child)'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        self.children.append(child)
        self._insert_into_sibling_maps(len(self.children) - 1, child)

    def invalidate_sibling_maps(self) -> None:
        self.prev_sibling_map: dict[int, NL | None] | None = None
        self.next_sibling_map: dict[int, NL | None] | None = None

    def _insert_into_sibling_maps(self, i: int, child: NL) -> None:
        """Splice a newly inserted child into the cached sibling maps.

        Keeps the maps valid without rebuilding them from scratch, which would
        be O(len(children)) per call and quadratic when many children are
        inserted while siblings are read in between (e.g. ``append_leaves``).
        """
        prev_map = self.prev_sibling_map
        next_map = self.next_sibling_map
        if prev_map is None or next_map is None:
            return
        before = self.children[i - 1] if i > 0 else None
        after = self.children[i + 1] if i + 1 < len(self.children) else None
        prev_map[id(child)] = before
        next_map[id(child)] = after
        next_map[id(before)] = child
        if after is not None:
            prev_map[id(after)] = child

    def _remove_from_sibling_maps(self, child: NL) -> None:
        """Splice a removed child out of the cached sibling maps."""
        prev_map = self.prev_sibling_map
        next_map = self.next_sibling_map
        if prev_map is None or next_map is None:
            return
        if id(child) not in prev_map:
            self.invalidate_sibling_maps()
            return
        before = prev_map.pop(id(child))
        after = next_map.pop(id(child))
        next_map[id(before)] = after
        if after is not None:
            prev_map[id(after)] = before

    def _replace_in_sibling_maps(self, old: NL, child: NL) -> None:
        """Swap ``old`` for ``child`` at the same position in the sibling maps."""
        prev_map = self.prev_sibling_map
        next_map = self.next_sibling_map
        if prev_map is None or next_map is None:
            return
        if id(old) not in prev_map:
            self.invalidate_sibling_maps()
            return
        before = prev_map.pop(id(old))
        after = next_map.pop(id(old))
        prev_map[id(child)] = before
        next_map[id(child)] = after
        next_map[id(before)] = child
        if after is not None:
            prev_map[id(after)] = child

    def _replace_child_in_sibling_maps(self, old: NL, new_children: list[NL]) -> None:
        """Swap ``old`` for ``new_children`` at the same position in the maps."""
        prev_map = self.prev_sibling_map
        next_map = self.next_sibling_map
        if prev_map is None or next_map is None:
            return
        if id(old) not in prev_map:
            self.invalidate_sibling_maps()
            return
        before = prev_map.pop(id(old))
        after = next_map.pop(id(old))
        previous = before
        for child in new_children:
            prev_map[id(child)] = previous
            next_map[id(previous)] = child
            previous = child
        next_map[id(previous)] = after
        if after is not None:
            prev_map[id(after)] = previous

    def update_sibling_maps(self) -> None:
        _prev: dict[int, NL | None] = {}
        _next: dict[int, NL | None] = {}
        self.prev_sibling_map = _prev
        self.next_sibling_map = _next
        previous: NL | None = None
        for current in self.children:
            _prev[id(current)] = previous
            _next[id(previous)] = current
            previous = current
        _next[id(current)] = None


class Leaf(Base):
    """Concrete implementation for leaf nodes."""

    value: str
    bracket_depth: int = 0

    # Changed later in brackets.py
    opening_bracket: Optional["Leaf"] = None

    _prefix = ""  # Whitespace and comments preceding this token in the input
    lineno: int = 0  # Line where this token starts in the input
    column: int = 0  # Column where this token starts in the input

    # clone() shares the below fields verbatim
    # These fields must either be immutable or not mutated, so as to prevent
    # leaves from spookily affecting each other

    # If not None, this Leaf is created by converting a block of fmt off/skip code.
    # The first Leaf in the converted code
    # Use read-only
    fmt_pass_converted_first_leaf: Optional["Leaf"] = None

    # Metadata for STANDALONE_COMMENT leaves converted from unchanged code for --line-ranges.
    # The converted block's first physical line
    line_ranges_first_lineno: int = 0
    # The requested physical source lines; can be before `first_lineno`
    line_ranges_selected: Optional[frozenset[int]] = None

    def __init__(
        self,
        type: int,
        value: str,
        context: Context | None = None,
        prefix: str | None = None,
        opening_bracket: Optional["Leaf"] = None,
        fmt_pass_converted_first_leaf: Optional["Leaf"] = None,
        bracket_depth: int = 0,
        line_ranges_first_lineno: int = 0,
        line_ranges_selected: Optional[frozenset[int]] = None,
    ) -> None:
        """
        Initializer.

        Takes a type constant (a token number < 256), a string value, and an
        optional context keyword argument.
        """

        assert 0 <= type < 256, type
        if context is not None:
            self._prefix, (self.lineno, self.column) = context
        self.type = type
        self.value = value
        if prefix is not None:
            self._prefix = prefix
        self.children = []
        self.opening_bracket = opening_bracket
        self.fmt_pass_converted_first_leaf = fmt_pass_converted_first_leaf
        self.bracket_depth = bracket_depth
        self.line_ranges_first_lineno = line_ranges_first_lineno
        self.line_ranges_selected = line_ranges_selected

    def __repr__(self) -> str:
        """Return a canonical string representation."""
        from .pgen2.token import tok_name

        assert self.type is not None
        return (
            f"{self.__class__.__name__}({tok_name.get(self.type, self.type)},"
            f" {self.value!r})"
        )

    def __str__(self) -> str:
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        return self._prefix + str(self.value)

    def _eq(self, other: "Leaf") -> bool:
        """Compare two nodes for equality."""
        return (self.type, self.value) == (other.type, other.value)

    def clone(self) -> "Leaf":
        assert self.type is not None
        """Return a cloned (deep) copy of self."""
        return Leaf(
            self.type,
            self.value,
            (self.prefix, (self.lineno, self.column)),
            fmt_pass_converted_first_leaf=self.fmt_pass_converted_first_leaf,
            bracket_depth=self.bracket_depth,
            line_ranges_first_lineno=self.line_ranges_first_lineno,
            line_ranges_selected=self.line_ranges_selected,
        )

    def leaves(self) -> Iterator["Leaf"]:
        yield self

    def pre_order(self) -> Iterator["Leaf"]:
        """Return a pre-order iterator for the tree."""
        yield self

    @property
    def prefix(self) -> str:
        """
        The whitespace and comments preceding this token in the input.
        """
        return self._prefix

    @prefix.setter
    def prefix(self, prefix: str) -> None:
        self._prefix = prefix


def convert(gr: Grammar, raw_node: RawNode) -> NL:
    """
    Convert raw node information to a Node or Leaf instance.

    This is passed to the parser driver which calls it whenever a reduction of a
    grammar rule produces a new complete node, so that the tree is build
    strictly bottom-up.
    """
    type, value, context, children = raw_node
    if children or type in gr.number2symbol:
        # If there's exactly one child, return that child instead of
        # creating a new node.
        assert children is not None
        if len(children) == 1:
            return children[0]
        return Node(type, children)
    else:
        return Leaf(type, value or "", context=context)
