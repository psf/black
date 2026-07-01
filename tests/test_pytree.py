"""Tests for blib2to3 concrete syntax trees."""

from blib2to3.pgen2 import token
from blib2to3.pytree import Leaf


def test_leaf_initializes_bracket_metadata() -> None:
    leaf = Leaf(token.NAME, "name")

    assert leaf.bracket_depth == 0
    assert leaf.opening_bracket is None
