import re
from collections.abc import Iterator
from dataclasses import replace
from typing import Any
from unittest.mock import patch

import pytest

import black
from black.mode import TargetVersion
from tests.util import (
    CaseId,
    FormatFailure,
    all_data_cases,
    assert_format,
    dump_to_stderr,
    find_cell,
    get_case_path,
    read_data,
    read_data_with_mode,
)


def _case_id(case: CaseId) -> str:
    if isinstance(case, tuple):
        stem, cell = case
        return f"{stem}::{cell}"
    return case


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("black.dump_to_file", dump_to_stderr):
        yield


def check_file(subdir: str, filename: CaseId, *, data: bool = True) -> None:
    args, source, expected = read_data_with_mode(subdir, filename, data=data)
    try:
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
    except (AssertionError, FormatFailure) as e:
        if not isinstance(filename, tuple):
            raise
        stem, cell_name = filename
        path = get_case_path(subdir, stem, data=data)
        target = find_cell(path, cell_name)
        if target is not None:
            header = f"\ncell `{cell_name}` at {path}:{target.header_lineno}"
            if target.output_lineno is not None:
                header += f"\n# output marker at {path}:{target.output_lineno}"
            else:
                header += "\n(idempotency cell, no `# output` marker)"
        else:
            header = f"\ncell `{cell_name}` at {path}"
        raise type(e)(f"{header}\n{e}") from e


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
@pytest.mark.parametrize("filename", all_data_cases("cases"), ids=_case_id)
def test_simple_format(filename: CaseId) -> None:
    check_file("cases", filename)


@pytest.mark.parametrize(
    "filename", all_data_cases("line_ranges_formatted"), ids=_case_id
)
def test_line_ranges_line_by_line(filename: CaseId) -> None:
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

    exc_info.match(
        re.escape(
            "Cannot parse for target version Python 3.10: 10:11\n"
            "        case a := b:\n"
            "              ^\n"
            "ParseError: bad input"
        )
    )
