import difflib
from collections.abc import Collection, Iterator, Sequence
from typing import List, Set, Tuple


def parse_line_ranges(line_ranges: Sequence[str]) -> List[Tuple[int, int]]:
    lines = []
    for lines_str in line_ranges:
        try:
            start, end = map(int, lines_str.split("-"))
            lines.append((start, end))
        except ValueError:
            raise ValueError(f"Incorrect --line-ranges format: {lines_str!r}")
    return lines


def is_valid_line_range(lines: Tuple[int, int]) -> bool:
    return lines[0] <= lines[1]


def sanitized_lines(lines: Collection[Tuple[int, int]], src_contents: str) -> Collection[Tuple[int, int]]:
    if not src_contents:
        return []

    src_line_count = src_contents.count("\n") + (not src_contents.endswith("\n"))
    return [(max(1, start), min(end, src_line_count)) for start, end in lines if start <= src_line_count]


def adjusted_lines(lines: Collection[Tuple[int, int]], original_source: str, modified_source: str) -> List[Tuple[int, int]]:
    lines_mappings = _calculate_lines_mappings(original_source, modified_source)
    new_lines, current_mapping_index = [], 0

    for start, end in sorted(lines):
        start_idx = _find_lines_mapping_index(start, lines_mappings, current_mapping_index)
        end_idx = _find_lines_mapping_index(end, lines_mappings, start_idx)

        if start_idx >= len(lines_mappings) or end_idx >= len(lines_mappings):
            continue

        start_map, end_map = lines_mappings[start_idx], lines_mappings[end_idx]
        new_start = start_map.modified_start if start_map.is_changed_block else start - start_map.original_start + start_map.modified_start
        new_end = end_map.modified_end if end_map.is_changed_block else end - end_map.original_start + end_map.modified_start

        if is_valid_line_range((new_start, new_end)):
            new_lines.append((new_start, new_end))

    return new_lines


def convert_unchanged_lines(src_node, lines: Collection[Tuple[int, int]]) -> None:
    lines_set: Set[int] = {line for start, end in lines for line in range(start, end + 1)}
    visitor = _TopLevelStatementsVisitor(lines_set)
    list(visitor.visit(src_node))
    _convert_unchanged_line_by_line(src_node, lines_set)


class _TopLevelStatementsVisitor:
    def __init__(self, lines_set: Set[int]):
        self._lines_set = lines_set

    def visit_simple_stmt(self, node) -> Iterator[None]:
        if last_leaf := last_leaf(node):
            ancestor = furthest_ancestor_with_last_leaf(last_leaf)
            if not _get_line_range(ancestor).intersection(self._lines_set):
                _convert_node_to_standalone_comment(ancestor)
        yield from []

    def visit_suite(self, node) -> Iterator[None]:
        if _contains_standalone_comment(node):
            return

        semantic_parent = node.parent
        if semantic_parent and semantic_parent.prev_sibling and semantic_parent.prev_sibling.type == ASYNC:
            semantic_parent = semantic_parent.parent

        if semantic_parent and not _get_line_range(semantic_parent).intersection(self._lines_set):
            _convert_node_to_standalone_comment(semantic_parent)
        yield from []
