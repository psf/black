from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

import black.concurrency as concurrency
from black import Mode, WriteBack
from black.report import Report


class FakeManager:
    shutdown_called: bool

    def __init__(self) -> None:
        self.shutdown_called = False

    def Lock(self) -> object:
        return object()

    def shutdown(self) -> None:
        self.shutdown_called = True


def test_manager_shutdown_called_for_diff(monkeypatch: Any, tmp_path: Path) -> None:
    """
    schedule_formatting() creates multiprocessing.Manager() for DIFF/COLOR_DIFF
    and must shut it down deterministically.
    """
    fake_manager = FakeManager()

    monkeypatch.setattr(concurrency, "Manager", lambda: fake_manager)

    def fake_format_file_in_place(
        src: Path,
        fast: bool,
        mode: Mode,
        write_back: WriteBack,
        lock: Optional[object],
    ) -> bool:
        assert lock is not None
        return False

    monkeypatch.setattr(concurrency, "format_file_in_place", fake_format_file_in_place)

    src = tmp_path / "a.py"
    src.write_text("x=1\n", encoding="utf8")

    async def run() -> None:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            await concurrency.schedule_formatting(
                sources={src},
                fast=False,
                write_back=WriteBack.DIFF,
                mode=Mode(),
                report=Report(),
                loop=loop,
                executor=executor,
                no_cache=True,
            )

    asyncio.run(run())

    assert fake_manager.shutdown_called is True
