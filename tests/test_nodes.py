"""Test the black.nodes module."""

import pytest

from black import Leaf, Mode, token
from black.nodes import is_type_comment


@pytest.mark.parametrize(
    "comment_text, expected",
    [
        ("# type: int", True),
        ("#type:int", True),
        ("#   type:    str", True),
        ("# type   :List[int]", False),
        ("#    type   :    Dict[str, Any]", False),
        ("#type :", False),
        ("#type:   ", True),
        ("#", False),
        ("# some other comment type: ", False),
        ("# type", False),
        ("# type:", True),
        ("#  type  :", False),
    ],
)
def test_is_type_comment(comment_text: str, expected: bool) -> None:
    leaf = Leaf(token.COMMENT, comment_text)
    mode = Mode(preview=True)
    assert is_type_comment(leaf=leaf, mode=mode) == expected
