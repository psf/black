"""Test the black.ranges module."""

from typing import List, Tuple

import pytest

from black.ranges import adjusted_lines


@pytest.mark.parametrize(
    "lines",
    [[(1, 1)], [(1, 3)], [(1, 1), (3, 4)]],
)
def test_no_diff(lines: List[Tuple[int, int]]) -> None:
    source = """\
import re

def func():
pass
"""
    assert lines == adjusted_lines(lines, source, source)


@pytest.mark.parametrize(
    "lines",
    [
        [(1, 0)],
        [(-8, 0)],
        [(-8, 8)],
        [(1, 100)],
        [(2, 1)],
        [(0, 8), (3, 1)],
    ],
)
def test_invalid_lines(lines: List[Tuple[int, int]]) -> None:
    original_source = """\
import re
def foo(arg):
'''This is the foo function.

This is foo function's
docstring with more descriptive texts.
'''

def func(arg1,
arg2, arg3):
pass
"""
    modified_source = """\
import re
def foo(arg):
'''This is the foo function.

This is foo function's
docstring with more descriptive texts.
'''

def func(arg1, arg2, arg3):
pass
"""
    assert not adjusted_lines(lines, original_source, modified_source)


@pytest.mark.parametrize(
    "lines,adjusted",
    [
        (
            [(1, 1)],
            [(1, 1)],
        ),
        (
            [(1, 2)],
            [(1, 1)],
        ),
        (
            [(1, 6)],
            [(1, 2)],
        ),
        (
            [(6, 6)],
            [],
        ),
    ],
)
def test_removals(
    lines: List[Tuple[int, int]], adjusted: List[Tuple[int, int]]
) -> None:
    original_source = """\
1. first line
2. second line
3. third line
4. fourth line
5. fifth line
6. sixth line
"""
    modified_source = """\
2. second line
5. fifth line
"""
    assert adjusted == adjusted_lines(lines, original_source, modified_source)


@pytest.mark.parametrize(
    "lines,adjusted",
    [
        (
            [(1, 1)],
            [(2, 2)],
        ),
        (
            [(1, 2)],
            [(2, 5)],
        ),
        (
            [(2, 2)],
            [(5, 5)],
        ),
    ],
)
def test_additions(
    lines: List[Tuple[int, int]], adjusted: List[Tuple[int, int]]
) -> None:
    original_source = """\
1. first line
2. second line
"""
    modified_source = """\
this is added
1. first line
this is added
this is added
2. second line
this is added
"""
    assert adjusted == adjusted_lines(lines, original_source, modified_source)


@pytest.mark.parametrize(
    "lines,adjusted",
    [
        (
            [(1, 11)],
            [(1, 10)],
        ),
        (
            [(1, 12)],
            [(1, 11)],
        ),
        (
            [(10, 10)],
            [(9, 9)],
        ),
        ([(1, 1), (9, 10)], [(1, 1), (9, 9)]),
        ([(9, 10), (1, 1)], [(1, 1), (9, 9)]),
    ],
)
def test_diffs(lines: List[Tuple[int, int]], adjusted: List[Tuple[int, int]]) -> None:
    original_source = """\
 1. import re
 2. def foo(arg):
 3.   '''This is the foo function.
 4.
 5.   This is foo function's
 6.   docstring with more descriptive texts.
 7.   '''
 8.
 9. def func(arg1,
10.   arg2, arg3):
11.   pass
12. # last line
"""
    modified_source = """\
 1. import re  # changed
 2. def foo(arg):
 3.   '''This is the foo function.
 4.
 5.   This is foo function's
 6.   docstring with more descriptive texts.
 7.   '''
 8.
 9. def func(arg1, arg2, arg3):
11.   pass
12. # last line changed
"""
    assert adjusted == adjusted_lines(lines, original_source, modified_source)
