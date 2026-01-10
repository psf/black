import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import black.concurrency as concurrency
from black import Mode, WriteBack


class FakeManager:
    def __init__(self):
        self.shutdown_called = False

    def Lock(self):
        return object()

    def shutdown(self):
        self.shutdown_called = True


class DummyReport:
    verbose = False

    def done(self, src, changed):
        pass

    def failed(self, src, message):
        raise AssertionError(f"Unexpected failure for {src}: {message}")


def test_manager_shutdown_called_for_diff(monkeypatch, tmp_path: Path):
    """
    Repro for #4950:
    schedule_formatting() creates multiprocessing.Manager() for DIFF/COLOR_DIFF
    but must shut it down deterministically.
    """
    fake_manager = FakeManager()

    monkeypatch.setattr(concurrency, "Manager", lambda: fake_manager)

    def fake_format_file_in_place(src, fast, mode, write_back, lock):
        assert lock is not None
        return False

    monkeypatch.setattr(concurrency, "format_file_in_place", fake_format_file_in_place)

    src = tmp_path / "a.py"
    src.write_text("x=1\n", encoding="utf8")

    async def run():
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            await concurrency.schedule_formatting(
                sources={src},
                fast=False,
                write_back=WriteBack.DIFF,
                mode=Mode(),
                report=DummyReport(),
                loop=loop,
                executor=executor,
                no_cache=True,
            )

    asyncio.run(run())

    # Fails BEFORE fix
    assert fake_manager.shutdown_called is True
