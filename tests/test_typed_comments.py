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


@pytest.mark.parametrize(
    "comment_str",
    [
        "# Not a type comment: for sure.",
        "# this is a comment about a :param called type",
        "#type : the first space is mandatory",
    ],
)
def test_not_typed_comments(comment_str: str) -> None:
    assert not is_type_comment(Leaf(token.COMMENT, comment_str))
