"""Functions related to Black's formatting by line ranges feature."""

from typing import (
    Collection,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    Iterator,
)

from blib2to3.pgen2.token import ASYNC, NEWLINE
from black.nodes import (
    first_leaf,
    furthest_ancestor_with_last_leaf,
    last_leaf,
    Leaf,
        LN,
    Node,
    STANDALONE_COMMENT,
    syms,
    Visitor,
)


def     convert_unchanged_lines(src_node: Node, lines: Collection[Tuple[int, int]]):
    """Converts unchanged lines to STANDALONE_COMMENT.

    The idea is similar to `# fmt: on/off` is implemented. It also converts the
    nodes between those markers as a single `STANDALONE_COMMENT` leaf node with
    the unformatted code as its value. `STANDALONE_COMMENT` is a "fake" token
    that will be formatted as-is with its prefix normalized.

    Here we perform two passes:

    1. Visit the top-level statements, and convert them to a single
       `STANDALONE_COMMENT` when unchanged. This speeds up formatting when some
       of the top-level statements aren't changed.
    2. Convert unchanged "unwrapped lines" to `STANDALONE_COMMENT` nodes line by
       line. "unwrapped lines" are divided by the `NEWLINE` token. e.g. a
       multi-line statement is *one* "unwrapped line" that ends with `NEWLINE`,
       even though this statement itself can span multiple lines, and the
       tokenizer only sees the last '\n' as the `NEWLINE` token.

    NOTE: During pass (2), comment prefixes and indentations are ALWAYS
    normalized even when the lines aren't changed. This is fixable by moving
    more formatting to pass (1). However, it's hard to get it correct when
    incorrect indentations are used. So we defer this to future optimizations.
    """
    lines_set: Set[int] = set()
    for start, end in lines:
        lines_set.update(range(start, end + 1))
    visitor = _TopLevelStatementsVisitor(lines_set)
    _ = list(visitor.visit(src_node))  # Consume all results.
    _convert_unchanged_line_by_line(src_node, lines_set)


def _contains_standalone_comment(node: LN) -> bool:
    if isinstance(node, Leaf):
        return node.type == STANDALONE_COMMENT
    else:
        for child in node.children:
            if _contains_standalone_comment(child):
                return True
        return False


class _TopLevelStatementsVisitor(Visitor[None]):
    """A node visitor that converts unchanged top-level statements to STANDALONE_COMMENT.

    This is used in addition to _convert_unchanged_lines_by_flatterning, to
    speed up formatting when there are unchanged top-level
    classes/functions/statements.
    """

    def __init__(self, lines_set: Set[int]):
        self._lines_set = lines_set

    def visit_simple_stmt(self, node: Node) -> Iterator[None]:
        # This is only called for top-level statements, since `visit_suite`
        # won't visit its children nodes.
        yield from []
        newline_leaf = last_leaf(node)
        if not newline_leaf:
            return
        assert (
            newline_leaf.type == NEWLINE
        ), f"Unexpectedly found leaf.type={newline_leaf.type}"
        # We need to find the furthest ancestor with the NEWLINE as the last
        # leaf, since a `suite` can simply be a `simple_stmt` when it puts
        # its body on the same line. Example: `if cond: pass`.
        ancestor = furthest_ancestor_with_last_leaf(newline_leaf)
        if not _get_line_range(ancestor).intersection(self._lines_set):
            _convert_node_to_standalone_comment(ancestor)

    def visit_suite(self, node: Node) -> Iterator[None]:
        yield from []
        # If there is a STANDALONE_COMMENT node, it means parts of the node tree
        # have fmt on/off/skip markers. Those STANDALONE_COMMENT nodes can't
        # be simply converted by calling str(node). So we just don't convert
        # here.
        if _contains_standalone_comment(node):
            return
        # Find the semantic parent of this suite. For `async_stmt` and
        # `async_funcdef`, the ASYNC token is defined on a separate level by the
        # grammar.
        semantic_parent = node.parent
        async_token: Optional[LN] = None
        if semantic_parent is not None:
            if (
                semantic_parent.prev_sibling is not None
                and semantic_parent.prev_sibling.type == ASYNC
            ):
                async_token = semantic_parent.prev_sibling
                semantic_parent = semantic_parent.parent
        if semantic_parent is not None and not _get_line_range(
            semantic_parent
        ).intersection(self._lines_set):
            _convert_node_to_standalone_comment(semantic_parent)


def _convert_unchanged_line_by_line(node: Node, lines_set: Set[int]):
    """Converts unchanged to STANDALONE_COMMENT line by line."""
    for leaf in node.leaves():
        if leaf.type != NEWLINE:
            # We only consider "unwrapped lines", which are divided by the NEWLINE
            # token.
            continue
        if leaf.parent and leaf.parent.type == syms.match_stmt:
            # The `suite` node is defined as:
            #   match_stmt: "match" subject_expr ':' NEWLINE INDENT case_block+ DEDENT
            # Here we need to check `subject_expr`. The `case_block+` will be
            # checked by their own NEWLINEs.
            nodes_to_ignore: List[LN] = []
            prev_sibling = leaf.prev_sibling
            while prev_sibling:
                nodes_to_ignore.insert(0, prev_sibling)
                prev_sibling = prev_sibling.prev_sibling
            if not nodes_to_ignore:
                assert False, "Unexpected empty nodes in the match_stmt"
                continue
            if not _get_line_range(nodes_to_ignore).intersection(lines_set):
                _convert_nodes_to_standalone_comment(nodes_to_ignore, newline=leaf)
        elif leaf.parent and leaf.parent.type == syms.suite:
            # The `suite` node is defined as:
            #   suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
            # We will check `simple_stmt` and `stmt+` separately against the lines set
            parent_sibling = leaf.parent.prev_sibling
            nodes_to_ignore = []
            while parent_sibling and not parent_sibling.type == syms.suite:
                # NOTE: Multiple suite nodes can exist as siblings in e.g. `if_stmt`.
                nodes_to_ignore.insert(0, parent_sibling)
                parent_sibling = parent_sibling.prev_sibling
            if not nodes_to_ignore:
                assert False, "Unexpected empty nodes before suite"
                continue
            # Special case for `async_stmt` and `async_funcdef` where the ASYNC
            # token is on the grandparent node.
            grandparent = leaf.parent.parent
            if (
                grandparent is not None
                and grandparent.prev_sibling is not None
                and grandparent.prev_sibling.type == ASYNC
            ):
                nodes_to_ignore.insert(0, grandparent.prev_sibling)
            if not _get_line_range(nodes_to_ignore).intersection(lines_set):
                _convert_nodes_to_standalone_comment(nodes_to_ignore, newline=leaf)
        else:
            ancestor = furthest_ancestor_with_last_leaf(leaf)
            # Consider multiple decorators as a whole block, as their
            # newlines have different behaviors than the rest of the grammar.
            if (
                ancestor.type == syms.decorator
                and ancestor.parent
                and ancestor.parent.type == syms.decorators
            ):
                ancestor = ancestor.parent
            if not _get_line_range(ancestor).intersection(lines_set):
                _convert_node_to_standalone_comment(ancestor)


def _convert_node_to_standalone_comment(node: LN):
    """Convert node to STANDALONE_COMMENT by modifying the tree inline."""
    parent = node.parent
    if not parent:
        return
    first = first_leaf(node)
    last = last_leaf(node)
    if not first or not last:
        assert False, "Unexpected empty first_leaf or last_leaf"
        return
    if first is last:
        # This can happen on the following edge cases:
        # 1. A block of `# fmt: off/on` code except the `# fmt: on` is placed
        #    on the end of the last line instead of on a new line.
        # 2. A single backslash on its own line followed by a comment line.
        # Ideally we don't want to format them when not requested, but fixing
        # isn't easy. These cases are also badly formatted code, so it isn't
        # too bad we reformat them.
        return
    # The prefix contains comments and indentation whitespaces. They are
    # reformatted accordingly to the correct indentation level.
    # This also means the indentation will be changed on the unchanged lines, and
    # this is actually required to not break incremental reformatting.
    prefix = first.prefix
    first.prefix = ""
    index = node.remove()
    if index is not None:
        # Remove the '\n', as STANDALONE_COMMENT will have '\n' appended when
        # genearting the formatted code.
        value = str(node)[:-1]
        parent.insert_child(
            index,
            Leaf(
                STANDALONE_COMMENT,
                value,
                prefix=prefix,
                fmt_pass_converted_first_leaf=first,
            ),
        )


def _convert_nodes_to_standalone_comment(nodes: Sequence[LN], *, newline: Leaf):
    """Convert nodes to STANDALONE_COMMENT by modifying the tree inline."""
    if not nodes:
        return
    parent = nodes[0].parent
    first = first_leaf(nodes[0])
    if not parent or not first:
        return
    prefix = first.prefix
    first.prefix = ""
    value = "".join(str(node) for node in nodes)
    # The prefix comment on the NEWLINE leaf is the trailing comment of the statement.
    if newline.prefix:
        value += newline.prefix
        newline.prefix = ""
    index = nodes[0].remove()
    for node in nodes[1:]:
        node.remove()
    if index is not None:
        parent.insert_child(
            index,
            Leaf(
                STANDALONE_COMMENT,
                value,
                prefix=prefix,
                fmt_pass_converted_first_leaf=first,
            ),
        )


def _leaf_line_end(leaf: Leaf) -> int:
    """Returns the line number of the leaf node's last line."""
    if leaf.type == NEWLINE:
        return leaf.lineno
    else:
        # Leaf nodes like multiline strings can occupy multiple lines.
        return leaf.lineno + str(leaf).count("\n")


def _get_line_range(node_or_nodes: Union[LN, List[LN]]) -> Set[int]:
    """Returns the line range of this node or list of nodes."""
    if isinstance(node_or_nodes, list):
        nodes = node_or_nodes
        if not nodes:
            return set()
        first = first_leaf(nodes[0])
        last = last_leaf(nodes[-1])
        if first and last:
            line_start = first.lineno
            line_end = _leaf_line_end(last)
            return set(range(line_start, line_end + 1))
        else:
            return set()
    else:
        node = node_or_nodes
        if isinstance(node, Leaf):
            return set(range(node.lineno, _leaf_line_end(node) + 1))
        else:
            first = first_leaf(node)
            last = last_leaf(node)
            if first and last:
                return set(range(first.lineno, _leaf_line_end(last) + 1))
            else:
                return set()
