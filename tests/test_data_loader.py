"""Unit tests for the multi-cell fixture loader in tests/util.py.

These exercise the loader against in-memory file content rather than the real
fixtures under tests/data/cases/, so regressions in cell parsing show up here
without depending on a specific fixture file.
"""

from __future__ import annotations

import textwrap
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests import util
from tests.util import (
    Cell,
    find_cell,
    is_multi_cell,
    parse_cells,
    read_data,
    read_data_with_mode,
    try_parse_cells,
)


@pytest.fixture(autouse=True)
def _clear_parse_cache() -> Iterator[None]:
    """`try_parse_cells` caches parse results by Path identity for the test
    session. Tests here reuse `tmp_path`-derived filenames across runs, so the
    cache is cleared before and after each test."""
    try_parse_cells.cache_clear()
    yield
    try_parse_cells.cache_clear()


@pytest.fixture
def patch_data_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Point `util.DATA_DIR` at a fresh temp dir for `read_data_with_mode`
    callers, with automatic restoration. Also pre-creates the subdirs that
    test_format.py's module-load parametrize decorators expect, so that
    importing it from within a test (e.g. to reach `check_file`) does not
    blow up on a missing `cases/` or `line_ranges_formatted/`."""
    monkeypatch.setattr(util, "DATA_DIR", tmp_path)
    (tmp_path / "cases").mkdir(exist_ok=True)
    (tmp_path / "line_ranges_formatted").mkdir(exist_ok=True)
    return tmp_path


def write(target_dir: Path, name: str, body: str) -> Path:
    path = target_dir / name
    path.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf8")
    return path


def test_single_case_file_returns_none(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        # flags: --preview
        x = 1
        # output
        x = 1
        """,
    )
    assert parse_cells(path.read_text(encoding="utf8"), path) is None


def test_file_with_case_header_not_at_top_is_single_case(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        x = 1
        [case nope]
        y = 2
        """,
    )
    assert parse_cells(path.read_text(encoding="utf8"), path) is None


def test_two_cells_parsed(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        # file-level prose

        [case alpha]
        import foo
        # output
        import foo

        [case beta]
        # flags: --pyi
        x: int
        # output
        x: int
        """,
    )
    cells = parse_cells(path.read_text(encoding="utf8"), path)
    assert cells is not None and len(cells) == 2
    assert cells[0].name == "alpha"
    assert cells[1].name == "beta"
    assert cells[0].args.mode.is_pyi is False
    assert cells[1].args.mode.is_pyi is True


def test_multi_cell_outputs_do_not_leak_between_cells(tmp_path: Path) -> None:
    """Each cell's `# output` marker bounds that cell's output. A second
    `[case ]` header ends the prior cell's output even if there's no blank
    line before it."""
    path = write(
        tmp_path,
        "fix.py",
        """
        [case first]
        a = 1
        # output
        a = 1

        [case second]
        b = 2
        # output
        b = 2
        """,
    )
    cells = parse_cells(path.read_text(encoding="utf8"), path)
    assert cells is not None and len(cells) == 2
    assert cells[0].input.strip() == "a = 1"
    assert cells[0].output.strip() == "a = 1"
    assert cells[1].input.strip() == "b = 2"
    assert cells[1].output.strip() == "b = 2"


def test_idempotency_cell_has_no_output_marker(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        [case lone]
        import bar
        """,
    )
    cells = parse_cells(path.read_text(encoding="utf8"), path)
    assert cells is not None and len(cells) == 1
    assert cells[0].input == cells[0].output
    assert cells[0].output_lineno is None


def test_duplicate_cell_name_raises(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        [case dup]
        x = 1
        [case dup]
        y = 2
        """,
    )
    with pytest.raises(ValueError, match="Duplicate cell name `dup`"):
        parse_cells(path.read_text(encoding="utf8"), path)


def test_header_tolerates_trailing_whitespace(tmp_path: Path) -> None:
    # Trailing spaces on a header should still be recognized — silently
    # treating the file as single-case is the worst failure mode.
    path = write(
        tmp_path,
        "fix.py",
        "[case foo]   \nx = 1\n",
    )
    cells = parse_cells(path.read_text(encoding="utf8"), path)
    assert cells is not None and len(cells) == 1
    assert cells[0].name == "foo"


def test_cell_flags_tolerate_leading_blank_lines(tmp_path: Path) -> None:
    # The docs promise `# flags: ` on the first *non-blank* line of a cell
    # body. A blank line between the `[case ]` header and the flags line must
    # not silently swallow the flags by parsing them as Python source.
    path = write(
        tmp_path,
        "fix.py",
        """
        [case foo]

        # flags: --preview
        x = 1
        # output
        x = 1
        """,
    )
    cells = parse_cells(path.read_text(encoding="utf8"), path)
    assert cells is not None and len(cells) == 1
    assert cells[0].args.mode.preview is True
    assert cells[0].input.strip() == "x = 1"


def test_single_case_flags_tolerate_leading_blank_lines(tmp_path: Path) -> None:
    # Single-case files share the same body parser. A blank line before the
    # `# flags: ` line at the top of a legacy single-case file must also be
    # tolerated.
    path = write(
        tmp_path,
        "fix.py",
        """

        # flags: --preview
        x = 1
        # output
        x = 1
        """,
    )
    from tests.util import read_data_from_file

    mode, input_text, output_text = read_data_from_file(path)
    assert mode.mode.preview is True
    assert input_text.strip() == "x = 1"
    assert output_text.strip() == "x = 1"


def test_header_accepts_mixed_case_and_numbers(tmp_path: Path) -> None:
    # Case names allow uppercase and trailing digits so contributors can name
    # cases after PEPs or issue numbers (`PEP_695`, `issue_4296_regression`).
    path = write(
        tmp_path,
        "fix.py",
        """
        [case PEP_695]
        x = 1
        [case issue_4296_regression]
        y = 2
        """,
    )
    cells = parse_cells(path.read_text(encoding="utf8"), path)
    assert cells is not None and [c.name for c in cells] == [
        "PEP_695",
        "issue_4296_regression",
    ]


def test_header_rejects_leading_whitespace(tmp_path: Path) -> None:
    # Leading whitespace must NOT make a header. Otherwise the detector and
    # the parser would disagree (detector says multi-cell, parser finds zero
    # headers), and all_data_cases would silently emit no tests.
    path = write(
        tmp_path,
        "fix.py",
        "   [case foo]\nx = 1\n",
    )
    assert parse_cells(path.read_text(encoding="utf8"), path) is None


def test_is_multi_cell_skips_leading_comments() -> None:
    lines = ["# a file-level comment\n", "\n", "[case x]\n"]
    assert is_multi_cell(lines) is True


def test_find_cell_returns_named_cell(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        [case alpha]
        x = 1
        [case beta]
        y = 2
        """,
    )
    cell = find_cell(path, "beta")
    assert cell is not None
    assert cell.name == "beta"
    assert cell.input.strip() == "y = 2"


def test_find_cell_missing_returns_none(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        [case alpha]
        x = 1
        """,
    )
    assert find_cell(path, "nope") is None


def test_find_cell_on_single_case_returns_none(tmp_path: Path) -> None:
    path = write(tmp_path, "fix.py", "x = 1\n")
    assert find_cell(path, "anything") is None


def test_try_parse_cells_returns_immutable_tuple(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "fix.py",
        """
        [case alpha]
        x = 1
        """,
    )
    result = try_parse_cells(path)
    assert result is not None
    assert isinstance(result, tuple)
    assert all(isinstance(c, Cell) for c in result)


def test_bare_stem_read_on_multi_cell_fails_loudly(patch_data_dir: Path) -> None:
    """Reading a multi-cell file by bare stem must raise. Callers have to
    pick a cell with the (stem, cell_name) tuple form."""
    cases_dir = patch_data_dir / "cases"
    write(
        cases_dir,
        "fix.py",
        """
        [case alpha]
        x = 1
        """,
    )
    with pytest.raises(AssertionError, match="bare-stem read of a multi-cell"):
        read_data_with_mode("cases", "fix")


def test_tuple_lookup_missing_cell_fails(patch_data_dir: Path) -> None:
    cases_dir = patch_data_dir / "cases"
    write(
        cases_dir,
        "fix.py",
        """
        [case alpha]
        x = 1
        """,
    )
    with pytest.raises(AssertionError, match="no cell named `missing`"):
        read_data_with_mode("cases", ("fix", "missing"))


def test_tuple_lookup_on_single_case_fails(patch_data_dir: Path) -> None:
    cases_dir = patch_data_dir / "cases"
    write(cases_dir, "fix.py", "x = 1\n")
    with pytest.raises(AssertionError, match="file is single-case"):
        read_data_with_mode("cases", ("fix", "alpha"))


def test_failing_cell_message_includes_cell_header(
    patch_data_dir: Path,
) -> None:
    """When a cell fails, the wrapped AssertionError must include the cell
    name and file location so the pytest traceback (which reads e.args[0])
    points the contributor at the right line."""
    cases_dir = patch_data_dir / "cases"
    fixture_path = write(
        cases_dir,
        "fix.py",
        """
        [case bad_cell]
        x = 1
        # output
        x = 2
        """,
    )
    # Lazy import to avoid module-level dependency from a unit-test file
    # onto the format harness.
    from tests.test_format import check_file

    with pytest.raises(AssertionError) as exc_info:
        check_file("cases", ("fix", "bad_cell"))

    message = str(exc_info.value)
    assert "cell `bad_cell`" in message
    assert str(fixture_path) in message
    assert "# output marker" in message


def test_per_cell_lookup_returns_isolated_input_output(
    patch_data_dir: Path,
) -> None:
    cases_dir = patch_data_dir / "cases"
    write(
        cases_dir,
        "fix.py",
        """
        [case first]
        a = 1
        # output
        a = 1

        [case second]
        b = 2
        # output
        b = 2
        """,
    )
    src, out = read_data("cases", ("fix", "second"))
    assert src.strip() == "b = 2"
    assert out.strip() == "b = 2"
