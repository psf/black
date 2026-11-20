from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

import black.concurrency as concurrency
from black import Mode, WriteBack
from black.report import Report


@pytest.mark.parametrize("no_cache", [False, True])
def test_schedule_larger_files_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, no_cache: bool
) -> None:
    small = tmp_path / "a_small.py"
    large_b = tmp_path / "b_large.py"
    large_c = tmp_path / "c_large.py"
    small.write_text("x = 1\n", encoding="utf8")
    large_b.write_text("x = 1\n" * 10, encoding="utf8")
    large_c.write_text("x = 2\n" * 10, encoding="utf8")
    formatted: list[Path] = []

    def format_file(src: Path, *args: Any) -> bool:
        formatted.append(src)
        return False

    monkeypatch.setattr(concurrency, "format_file_in_place", format_file)

    async def run() -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            await concurrency.schedule_formatting(
                sources={small, large_c, large_b},
                fast=False,
                write_back=WriteBack.CHECK,
                mode=Mode(),
                report=Report(),
                loop=asyncio.get_running_loop(),
                executor=executor,
                no_cache=no_cache,
                cache_dir=tmp_path / "cache",
            )

    asyncio.run(run())
    assert formatted == [large_b, large_c, small]


def test_schedule_missing_file_does_not_abort_other_files(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    source.write_text("x = 1\n", encoding="utf8")
    missing = tmp_path / "missing.py"
    report = Report()

    async def run() -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            await concurrency.schedule_formatting(
                sources={missing, source},
                fast=False,
                write_back=WriteBack.CHECK,
                mode=Mode(),
                report=report,
                loop=asyncio.get_running_loop(),
                executor=executor,
                no_cache=True,
            )

    asyncio.run(run())
    assert report.failure_count == 1
    assert report.same_count == 1
    assert report.return_code == 123
