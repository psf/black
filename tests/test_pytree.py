"""Tests for blib2to3 pytree nodes and leaves."""

import pickle

import pytest

from blib2to3.pgen2 import token
from blib2to3.pytree import Base, Leaf, Node


def test_slots_eliminate_instance_dict() -> None:
    """Verify that Base, Node, and Leaf use __slots__ and have no __dict__."""
    assert hasattr(Base, "__slots__")
    assert hasattr(Node, "__slots__")
    assert hasattr(Leaf, "__slots__")

    leaf = Leaf(token.NAME, "x")
    node = Node(256, [leaf])

    assert not hasattr(leaf, "__dict__")
    assert not hasattr(node, "__dict__")

    with pytest.raises(AttributeError):
        leaf.unexpected_attribute = "disallowed"  # type: ignore[attr-defined]

    with pytest.raises(AttributeError):
        node.unexpected_attribute = "disallowed"  # type: ignore[attr-defined]


def test_leaf_defaults_and_attributes() -> None:
    """Verify default values and context unpacking on Leaf."""
    leaf = Leaf(token.NAME, "foo")
    assert leaf.type == token.NAME
    assert leaf.value == "foo"
    assert leaf.parent is None
    assert leaf.children == []
    assert leaf.prefix == ""
    assert leaf.lineno == 0
    assert leaf.column == 0
    assert leaf.bracket_depth == 0
    assert leaf.opening_bracket is None
    assert leaf.fmt_pass_converted_first_leaf is None
    assert leaf.line_ranges_first_lineno == 0
    assert leaf.line_ranges_selected is None

    # Context unpacking
    leaf_with_context = Leaf(token.NUMBER, "42", context=("    ", (12, 4)))
    assert leaf_with_context.prefix == "    "
    assert leaf_with_context.lineno == 12
    assert leaf_with_context.column == 4

    # Explicit prefix override
    leaf_with_prefix = Leaf(
        token.NUMBER, "42", context=("    ", (12, 4)), prefix="# c\n"
    )
    assert leaf_with_prefix.prefix == "# c\n"
    assert leaf_with_prefix.lineno == 12
    assert leaf_with_prefix.column == 4


def test_node_hierarchy_and_slots() -> None:
    """Verify Node hierarchy, sibling mappings, clone, and pickle roundtrip."""
    leaf1 = Leaf(token.NAME, "a")
    leaf2 = Leaf(token.PLUS, "+")
    leaf3 = Leaf(token.NAME, "b")
    node = Node(256, [leaf1, leaf2, leaf3])

    assert node.parent is None
    assert leaf1.parent is node
    assert leaf2.parent is node
    assert leaf3.parent is node

    # Siblings
    assert leaf1.next_sibling is leaf2
    assert leaf2.prev_sibling is leaf1
    assert leaf2.next_sibling is leaf3
    assert leaf3.prev_sibling is leaf2

    # Clone
    cloned = node.clone()
    assert not hasattr(cloned, "__dict__")
    assert not hasattr(cloned.children[0], "__dict__")
    assert cloned.type == node.type
    assert len(cloned.children) == len(node.children)
    assert cloned.children[0] is not leaf1
    assert cloned.children[0].parent is cloned

    # Pickle roundtrip
    pickled = pickle.dumps(node)
    unpickled: Node = pickle.loads(pickled)
    assert not hasattr(unpickled, "__dict__")
    assert not hasattr(unpickled.children[0], "__dict__")
    assert unpickled.type == node.type
    assert len(unpickled.children) == 3
    first_child = unpickled.children[0]
    assert isinstance(first_child, Leaf)
    assert first_child.value == "a"
