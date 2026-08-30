"""Regression test for Leaf.bracket_depth not being initialized.

See https://github.com/psf/black/issues/5214 — ``blib2to3.pytree.Leaf``
annotates ``bracket_depth`` as ``int`` but never initializes it in
``__init__``, so accessing ``leaf.bracket_depth`` raises ``AttributeError``.
This crashes ``black.lines.is_line_short_enough`` which reads
``leaf.bracket_depth``.
"""

from blib2to3.pytree import Leaf


def test_leaf_bracket_depth_is_initialized() -> None:
    """A freshly constructed Leaf must have a ``bracket_depth`` attribute."""
    leaf = Leaf(14, "str")
    assert hasattr(leaf, "bracket_depth")
    assert leaf.bracket_depth == 0


def test_leaf_opening_bracket_is_initialized() -> None:
    """A freshly constructed Leaf must have an ``opening_bracket`` attribute."""
    leaf = Leaf(14, "str")
    assert hasattr(leaf, "opening_bracket")
    assert leaf.opening_bracket is None