from __future__ import annotations

import asyncio
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

import pytest

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


def test_is_tempdir_too_long_for_unix_sockets(monkeypatch: Any) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/long" * 50)
    assert concurrency._is_tempdir_too_long_for_unix_sockets() is False

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/tmp")
    assert concurrency._is_tempdir_too_long_for_unix_sockets() is False

    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/var/folders/" + "a" * 80)
    assert concurrency._is_tempdir_too_long_for_unix_sockets() is True

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/tmp")
    assert concurrency._is_tempdir_too_long_for_unix_sockets() is False

    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/tmp/" + "a" * 80)
    assert concurrency._is_tempdir_too_long_for_unix_sockets() is True


def test_schedule_formatting_long_tempdir_error(
    monkeypatch: Any, tmp_path: Path
) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/very/long/temp/dir" * 10)

    err_messages: list[str] = []
    monkeypatch.setattr(concurrency, "err", lambda msg: err_messages.append(msg))

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

    with pytest.raises(SystemExit) as exc_info:
        asyncio.run(run())

    assert exc_info.value.code == 1
    assert any("AF_UNIX path limit" in m for m in err_messages)


@pytest.mark.parametrize(
    "exc",
    [OSError("AF_UNIX path too long"), EOFError()],
    ids=["oserror", "eoferror"],
)
def test_schedule_formatting_manager_failure_error(
    monkeypatch: Any, tmp_path: Path, exc: Exception
) -> None:
    def failing_manager() -> Any:
        raise exc

    monkeypatch.setattr(concurrency, "Manager", failing_manager)

    err_messages: list[str] = []
    monkeypatch.setattr(concurrency, "err", lambda msg: err_messages.append(msg))

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

    with pytest.raises(SystemExit) as exc_info:
        asyncio.run(run())

    assert exc_info.value.code == 1
    assert any(
        "Cannot start multiprocessing manager for --diff" in m for m in err_messages
    )
