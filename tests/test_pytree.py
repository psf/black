import copy

from blib2to3.pgen2 import token
from blib2to3.pytree import Leaf, Node


def test_deepcopy_leaf() -> None:
    leaf = Leaf(token.NAME, "x")
    copied = copy.deepcopy(leaf)
    assert copied == leaf
    assert copied is not leaf


def test_deepcopy_node() -> None:
    node = Node(256, [Leaf(token.NAME, "x"), Leaf(token.EQUAL, "=")])
    copied = copy.deepcopy(node)
    assert copied == node
    assert copied is not node
    assert copied.children[0] is not node.children[0]
    assert copied.children[1] is not node.children[1]
