"""Functions related to Black's formatting by line ranges feature."""

import difflib
from collections.abc import Collection, Iterator, Sequence
from dataclasses import dataclass
from typing import Union

from black.nodes import (
    LN,
    STANDALONE_COMMENT,
    Leaf,
    Node,
    Visitor,
    first_leaf,
    furthest_ancestor_with_last_leaf,
    last_leaf,
    syms,
)
from blib2to3.pgen2.token import ASYNC, NEWLINE


def parse_line_ranges(line_ranges: Sequence[str]) -> list[tuple[int, int]]:
    lines: list[tuple[int, int]] = []
    for lines_str in line_ranges:
        parts = lines_str.split("-")
        if len(parts) != 2:
            raise ValueError(
                "Incorrect --line-ranges format, expect 'START-END', found"
                f" {lines_str!r}"
            )
        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError:
            raise ValueError(
                "Incorrect --line-ranges value, expect integer ranges, found"
                f" {lines_str!r}"
            ) from None
        else:
            lines.append((start, end))
    return lines


def is_valid_line_range(lines: tuple[int, int]) -> bool:
    return not lines or lines[0] <= lines[1]


def sanitized_lines(
    lines: Collection[tuple[int, int]], src_contents: str
) -> Collection[tuple[int, int]]:
    if not src_contents:
        return []
    good_lines = []
    src_line_count = src_contents.count("\n")
    if not src_contents.endswith("\n"):
        src_line_count += 1
    for start, end in lines:
        if start > src_line_count:
            continue
        start = max(start, 1)
        if end < start:
            continue
        end = min(end, src_line_count)
        good_lines.append((start, end))
    return good_lines


def adjusted_lines(
    lines: Collection[tuple[int, int]],
    original_source: str,
    modified_source: str,
) -> list[tuple[int, int]]:
    lines_mappings = _calculate_lines_mappings(original_source, modified_source)
    new_lines = []
    current_mapping_index = 0
    for start, end in sorted(lines):
        start_mapping_index = _find_lines_mapping_index(
            start,
            lines_mappings,
            current_mapping_index,
        )
        end_mapping_index = _find_lines_mapping_index(
            end,
            lines_mappings,
            start_mapping_index,
        )
        current_mapping_index = start_mapping_index
        if start_mapping_index >= len(lines_mappings) or end_mapping_index >= len(
            lines_mappings
        ):
            continue
        start_mapping = lines_mappings[start_mapping_index]
        end_mapping = lines_mappings[end_mapping_index]
        new_start = (
            start - start_mapping.original_start + start_mapping.modified_start
            if not start_mapping.is_changed_block
            else start_mapping.modified_start
        )
        new_end = (
            end - end_mapping.original_start + end_mapping.modified_start
            if not end_mapping.is_changed_block
            else end_mapping.modified_end
        )
        new_range = (new_start, new_end)
        if is_valid_line_range(new_range):
            new_lines.append(new_range)
    return new_lines


def convert_unchanged_lines(src_node: Node, lines: Collection[tuple[int, int]]) -> None:
    lines_set: set[int] = set()
    for start, end in lines:
        lines_set.update(range(start, end + 1))
    visitor = _TopLevelStatementsVisitor(lines_set)
    _ = list(visitor.visit(src_node))
    _convert_unchanged_line_by_line(src_node, lines_set)


def _contains_standalone_comment(node: LN) -> bool:
    if isinstance(node, Leaf):
        return node.type == STANDALONE_COMMENT
    for child in node.children:
        if _contains_standalone_comment(child):
            return True
    return False


class _TopLevelStatementsVisitor(Visitor[None]):
    def __init__(self, lines_set: set[int]):
        self._lines_set = lines_set

    def visit_simple_stmt(self, node: Node) -> Iterator[None]:
        yield from []
        newline_leaf = last_leaf(node)
        if not newline_leaf:
            return
        assert (
            newline_leaf.type == NEWLINE
        ), f"Unexpectedly found leaf.type={newline_leaf.type}"
        ancestor = furthest_ancestor_with_last_leaf(newline_leaf)
        if not _get_line_range(ancestor).intersection(self._lines_set):
            _convert_node_to_standalone_comment(ancestor)

    def visit_suite(self, node: Node) -> Iterator[None]:
        yield from []
        if _contains_standalone_comment(node):
            return
        semantic_parent = node.parent
        if (
            semantic_parent
            and semantic_parent.prev_sibling
            and semantic_parent.prev_sibling.type == ASYNC
        ):
            semantic_parent = semantic_parent.parent
        if semantic_parent and not _get_line_range(
            semantic_parent
        ).intersection(self._lines_set):
            _convert_node_to_standalone_comment(semantic_parent)


def _convert_unchanged_line_by_line(node: Node, lines_set: set[int]) -> None:
    for leaf in node.leaves():
        if leaf.type != NEWLINE:
            continue
        if leaf.parent and leaf.parent.type == syms.match_stmt:
            nodes_to_ignore: list[LN] = []
            prev_sibling = leaf.prev_sibling
            while prev_sibling:
                nodes_to_ignore.insert(0, prev_sibling)
                prev_sibling = prev_sibling.prev_sibling
            if not _get_line_range(nodes_to_ignore).intersection(lines_set):
                _convert_nodes_to_standalone_comment(nodes_to_ignore, newline=leaf)
        elif leaf.parent and leaf.parent.type == syms.suite:
            parent_sibling = leaf.parent.prev_sibling
            nodes_to_ignore = []
            while parent_sibling and not parent_sibling.type == syms.suite:
                nodes_to_ignore.insert(0, parent_sibling)
                parent_sibling = parent_sibling.prev_sibling
            grandparent = leaf.parent.parent
            if (
                grandparent
                and grandparent.prev_sibling
                and grandparent.prev_sibling.type == ASYNC
            ):
                nodes_to_ignore.insert(0, grandparent.prev_sibling)
            if not _get_line_range(nodes_to_ignore).intersection(lines_set):
                _convert_nodes_to_standalone_comment(nodes_to_ignore, newline=leaf)
        else:
            ancestor = furthest_ancestor_with_last_leaf(leaf)
            if (
                ancestor.type == syms.decorator
                and ancestor.parent
                and ancestor.parent.type == syms.decorators
            ):
                ancestor = ancestor.parent
            if not _get_line_range(ancestor).intersection(lines_set):
                _convert_node_to_standalone_comment(ancestor)


def _convert_node_to_standalone_comment(node: LN) -> None:
    parent = node.parent
    if not parent:
        return
    first = first_leaf(node)
    last = last_leaf(node)
    if not first or not last or first is last:
        return
    prefix = first.prefix
    first.prefix = ""
    index = node.remove()
    if index is not None:
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


def _convert_nodes_to_standalone_comment(nodes: Sequence[LN], *, newline: Leaf) -> None:
    if not nodes:
        return
    parent = nodes[0].parent
    first = first_leaf(nodes[0])
    if not parent or not first:
        return
    prefix = first.prefix
    first.prefix = ""
    value = "".join(str(node) for node in nodes)
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
    return leaf.lineno if leaf.type == NEWLINE else leaf.lineno + str(leaf).count("\n")


def _get_line_range(node_or_nodes: Union[LN, list[LN]]) -> set[int]:
    if isinstance(node_or_nodes, list):
        nodes = node_or_nodes
        if not nodes:
            return set()
        first = first_leaf(nodes[0])
        last = last_leaf(nodes[-1])
        if first and last:
            return set(range(first.lineno, _leaf_line_end(last) + 1))
        return set()
    node = node_or_nodes
    if isinstance(node, Leaf):
        return set(range(node.lineno, _leaf_line_end(node) + 1))
    first = first_leaf(node)
    last = last_leaf(node)
    if first and last:
        return set(range(first.lineno, _leaf_line_end(last) + 1))
    return set()


@dataclass
class _LinesMapping:
    original_start: int
    original_end: int
    modified_start: int
    modified_end: int
    is_changed_block: bool


def _calculate_lines_mappings(
    original_source: str,
    modified_source: str,
) -> Sequence[_LinesMapping]:
    matcher = difflib.SequenceMatcher(
        None,
        original_source.splitlines(keepends=True),
        modified_source.splitlines(keepends=True),
    )
    matching_blocks = matcher.get_matching_blocks()
    lines_mappings: list[_LinesMapping] = []
    for i, block in enumerate(matching_blocks):
        if i == 0 and (block.a != 0 or block.b != 0):
            lines_mappings.append(
                _LinesMapping(
                    original_start=1,
                    original_end=block.a,
                    modified_start=1,
                    modified_end=block.b,
                    is_changed_block=False,
                )
            )
        else:
            previous_block = matching_blocks[i - 1]
            lines_mappings.append(
                _LinesMapping(
                    original_start=previous_block.a + previous_block.size + 1,
                    original_end=block.a,
                    modified_start=previous_block.b + previous_block.size + 1,
                    modified_end=block.b,
                    is_changed_block=True,
                )
            )
        if i < len(matching_blocks) - 1:
            lines_mappings.append(
                _LinesMapping(
                    original_start=block.a + 1,
                    original_end=block.a + block.size,
                    modified_start=block.b + 1,
                    modified_end=block.b + block.size,
                    is_changed_block=False,
                )
            )
    return lines_mappings


def _find_lines_mapping_index(
    original_line: int,
    lines_mappings: Sequence[_LinesMapping],
    start_index: int,
) -> int:
    index = start_index
    while index < len(lines_mappings):
        mapping = lines_mappings[index]
        if mapping.original_start <= original_line <= mapping.original_end:
            return index
        index += 1
    return index
