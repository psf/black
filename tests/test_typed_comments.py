import pytest

from black.nodes import is_type_comment
from blib2to3.pgen2 import token
from blib2to3.pytree import Leaf


@pytest.mark.parametrize(
    "comment_str",
    ["# type: int", "#  type: int", "#   type: int", "# type : int", "# type  : int"],
)
def test_typed_comments(comment_str: str) -> None:
    assert is_type_comment(Leaf(token.COMMENT, comment_str))
