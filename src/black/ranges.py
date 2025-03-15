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
    lines = []
    for lines_str in line_ranges:
        try:
            start, end = map(int, lines_str.split("-"))
            lines.append((start, end))
        except (ValueError, IndexError):
            raise ValueError(f"Incorrect --line-ranges format or value: {lines_str!r}")
    return lines


def is_valid_line_range(lines: tuple[int, int]) -> bool:
    return not lines or lines[0] <= lines[1]


def sanitized_lines(lines: Collection[tuple[int, int]], src_contents: str) -> Collection[tuple[int, int]]:
    if not src_contents:
        return []
    src_line_count = src_contents.count("\n") + (not src_contents.endswith("\n"))
    return [
        (max(start, 1), min(end, src_line_count))
        for start, end in lines
        if start <= src_line_count and end >= start
    ]


def adjusted_lines(lines: Collection[tuple[int, int]], original_source: str, modified_source: str) -> list[tuple[int, int]]:
    lines_mappings = _calculate_lines_mappings(original_source, modified_source)
    new_lines = []
    current_mapping_index = 0

    for start, end in sorted(lines):
        start_mapping_index = _find_lines_mapping_index(start, lines_mappings, current_mapping_index)
        end_mapping_index = _find_lines_mapping_index(end, lines_mappings, start_mapping_index)
        current_mapping_index = start_mapping_index

        if start_mapping_index >= len(lines_mappings) or end_mapping_index >= len(lines_mappings):
            continue

        start_mapping = lines_mappings[start_mapping_index]
        end_mapping = lines_mappings[end_mapping_index]

        new_start = start_mapping.modified_start if start_mapping.is_changed_block else start - start_mapping.original_start + start_mapping.modified_start
        new_end = end_mapping.modified_end if end_mapping.is_changed_block else end - end_mapping.original_start + end_mapping.modified_start

        if is_valid_line_range((new_start, new_end)):
            new_lines.append((new_start, new_end))

    return new_lines


def convert_unchanged_lines(src_node: Node, lines: Collection[tuple[int, int]]) -> None:
    lines_set = {line for start, end in lines for line in range(start, end + 1)}
    visitor = _TopLevelStatementsVisitor(lines_set)
    _ = list(visitor.visit(src_node))
    _convert_unchanged_line_by_line(src_node, lines_set)


def _contains_standalone_comment(node: LN) -> bool:
    return any(_contains_standalone_comment(child) for child in node.children) if not isinstance(node, Leaf) else node.type == STANDALONE_COMMENT


class _TopLevelStatementsVisitor(Visitor[None]):
    def __init__(self, lines_set: set[int]):
        self._lines_set = lines_set

    def visit_simple_stmt(self, node: Node) -> Iterator[None]:
        newline_leaf = last_leaf(node)
        if newline_leaf and newline_leaf.type == NEWLINE:
            ancestor = furthest_ancestor_with_last_leaf(newline_leaf)
            if not _get_line_range(ancestor).intersection(self._lines_set):
                _convert_node_to_standalone_comment(ancestor)

    def visit_suite(self, node: Node) -> Iterator[None]:
        if _contains_standalone_comment(node):
            return
        semantic_parent = node.parent
        if semantic_parent and semantic_parent.prev_sibling and semantic_parent.prev_sibling.type == ASYNC:
            semantic_parent = semantic_parent.parent
        if semantic_parent and not _get_line_range(semantic_parent).intersection(self._lines_set):
            _convert_node_to_standalone_comment(semantic_parent)


def _convert_unchanged_line_by_line(node: Node, lines_set: set[int]) -> None:
    for leaf in node.leaves():
        if leaf.type != NEWLINE:
            continue
        ancestor = furthest_ancestor_with_last_leaf(leaf)
        if ancestor.type == syms.decorator and ancestor.parent and ancestor.parent.type == syms.decorators:
            ancestor = ancestor.parent
        if not _get_line_range(ancestor).intersection(lines_set):
            _convert_node_to_standalone_comment(ancestor)


def _convert_node_to_standalone_comment(node: LN) -> None:
    parent = node.parent
    if not parent:
        return
    first, last = first_leaf(node), last_leaf(node)
    if not first or not last or first is last:
        return
    prefix = first.prefix
    first.prefix = ""
    index = node.remove()
    if index is not None:
        value = str(node)[:-1]
        parent.insert_child(index, Leaf(STANDALONE_COMMENT, value, prefix=prefix, fmt_pass_converted_first_leaf=first))


def _convert_nodes_to_standalone_comment(nodes: Sequence[LN], *, newline: Leaf) -> None:
    if not nodes:
        return
    parent, first = nodes[0].parent, first_leaf(nodes[0])
    if not parent or not first:
        return
    prefix = first.prefix
    first.prefix = ""
    value = "".join(str(node) for node in nodes) + (newline.prefix if newline.prefix else "")
    newline.prefix = ""
    index = nodes[0].remove()
    for node in nodes[1:]:
        node.remove()
    if index is not None:
        parent.insert_child(index, Leaf(STANDALONE_COMMENT, value, prefix=prefix, fmt_pass_converted_first_leaf=first))


def _leaf_line_end(leaf: Leaf) -> int:
    return leaf.lineno + str(leaf).count("\n") if leaf.type != NEWLINE else leaf.lineno


def _get_line_range(node_or_nodes: Union[LN, list[LN]]) -> set[int]:
    nodes = node_or_nodes if isinstance(node_or_nodes, list) else [node_or_nodes]
    if not nodes:
        return set()
    first, last = first_leaf(nodes[0]), last_leaf(nodes[-1])
    return set(range(first.lineno, _leaf_line_end(last) + 1)) if first and last else set()


@dataclass
class _LinesMapping:
    original_start: int
    original_end: int
    modified_start: int
    modified_end: int
    is_changed_block: bool


def _calculate_lines_mappings(original_source: str, modified_source: str) -> Sequence[_LinesMapping]:
    matcher = difflib.SequenceMatcher(None, original_source.splitlines(keepends=True), modified_source.splitlines(keepends=True))
    matching_blocks = matcher.get_matching_blocks()
    lines_mappings = []

    for i, block in enumerate(matching_blocks):
        if i == 0 and (block.a != 0 or block.b != 0):
            lines_mappings.append(_LinesMapping(1, block.a, 1, block.b, False))
        if i > 0:
            prev_block = matching_blocks[i - 1]
            lines_mappings.append(_LinesMapping(prev_block.a + prev_block.size + 1, block.a, prev_block.b + prev_block.size + 1, block.b, True))
        if i < len(matching_blocks) - 1:
            lines_mappings.append(_LinesMapping(block.a + 1, block.a + block.size, block.b + 1, block.b + block.size, False))

    return lines_mappings


def _find_lines_mapping_index(original_line: int, lines_mappings: Sequence[_LinesMapping], start_index: int) -> int:
    for index in range(start_index, len(lines_mappings)):
        mapping = lines_mappings[index]
        if mapping.original_start <= original_line <= mapping.original_end:
            return index
    return len(lines_mappings)