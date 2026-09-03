import pytest

from black.comments import contains_pragma_comment
from blib2to3.pgen2.token import COMMENT
from blib2to3.pytree import Leaf


def _comment_leaf(value: str) -> Leaf:
    return Leaf(COMMENT, value)


def test_ruff_ignore_is_pragma():
    """`# ruff: ignore[...]` should be treated as a pragma comment."""
    leaf = _comment_leaf("# ruff: ignore[bweh]")
    assert contains_pragma_comment([leaf]) is True


def test_ruff_ignore_no_space_is_pragma():
    """`# ruff:ignore[...]` (no space) should also be treated as a pragma."""
    leaf = _comment_leaf("# ruff:ignore[bweh]")
    assert contains_pragma_comment([leaf]) is True
