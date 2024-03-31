from dataclasses import replace
from typing import Any, Iterator
from unittest.mock import patch

import pytest

import black
from black.mode import TargetVersion
from tests.util import (
    all_data_cases,
    assert_format,
    dump_to_stderr,
    read_data,
    read_data_with_mode,
)


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("black.dump_to_file", dump_to_stderr):
        yield


def check_file(subdir: str, filename: str, *, data: bool = True) -> None:
    args, source, expected = read_data_with_mode(subdir, filename, data=data)
    assert_format(
        source,
        expected,
        args.mode,
        fast=args.fast,
        minimum_version=args.minimum_version,
        lines=args.lines,
        no_preview_line_length_1=args.no_preview_line_length_1,
    )
    if args.minimum_version is not None:
        major, minor = args.minimum_version
        target_version = TargetVersion[f"PY{major}{minor}"]
        mode = replace(args.mode, target_versions={target_version})
        assert_format(
            source,
            expected,
            mode,
            fast=args.fast,
            minimum_version=args.minimum_version,
            lines=args.lines,
            no_preview_line_length_1=args.no_preview_line_length_1,
        )


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
@pytest.mark.parametrize("filename", all_data_cases("cases"))
def test_simple_format(filename: str) -> None:
    check_file("cases", filename)


@pytest.mark.parametrize("filename", all_data_cases("line_ranges_formatted"))
def test_line_ranges_line_by_line(filename: str) -> None:
    args, source, expected = read_data_with_mode("line_ranges_formatted", filename)
    assert (
        source == expected
    ), "Test cases in line_ranges_formatted must already be formatted."
    line_count = len(source.splitlines())
    for line in range(1, line_count + 1):
        assert_format(
            source,
            expected,
            args.mode,
            fast=args.fast,
            minimum_version=args.minimum_version,
            lines=[(line, line)],
        )


# =============== #
# Unusual cases
# =============== #


def test_empty() -> None:
    source = expected = ""
    assert_format(source, expected)


def test_patma_invalid() -> None:
    source, expected = read_data("miscellaneous", "pattern_matching_invalid")
    mode = black.Mode(target_versions={black.TargetVersion.PY310})
    with pytest.raises(black.parsing.InvalidInput) as exc_info:
        assert_format(source, expected, mode, minimum_version=(3, 10))

    exc_info.match("Cannot parse: 10:11")
