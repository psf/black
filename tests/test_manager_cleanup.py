"""Tests for Manager cleanup in concurrency module - Bug Fix Verification"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from black import Mode, WriteBack
from black.concurrency import schedule_formatting
from black.report import Report


def run_async(coro: Any) -> Any:
    """Helper to run async function in sync test"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


class TestManagerCleanup:
    """Verify Manager is properly shutdown after use in schedule_formatting"""

    def test_manager_shutdown_called_on_success(self) -> None:
        """Test that Manager.shutdown() is called after successful execution

        This test FAILS on base commit (no shutdown)
        This test PASSES after solution (with shutdown in finally block)
        """

        async def run_test() -> None:
            with patch("black.concurrency.Manager") as mock_manager_class:
                # Setup mock Manager
                mock_manager = MagicMock()
                mock_lock = MagicMock()
                mock_manager.Lock.return_value = mock_lock
                mock_manager_class.return_value = mock_manager

                # Create mock executor and loop that returns completed futures
                loop = asyncio.get_event_loop()
                mock_executor = MagicMock()

                # Mock the executor to return a completed future
                from concurrent.futures import Future

                future = Future()
                future.set_result(False)  # Simulate no changes made
                mock_executor.submit.return_value = future

                # Provide actual source file to trigger manager creation
                with patch("black.concurrency.Cache.read", return_value=None):
                    await schedule_formatting(
                        sources={Path("test.py")},  # Actual source file
                        fast=False,
                        write_back=WriteBack.DIFF,
                        mode=Mode(),
                        report=Report(),
                        loop=loop,
                        executor=mock_executor,
                        no_cache=True,
                    )

                # CRITICAL ASSERTION: Manager.shutdown() MUST be called
                # This FAILS on base commit because shutdown is never called
                # This PASSES after solution when shutdown is in finally block
                mock_manager.shutdown.assert_called_once()

        run_async(run_test())

    def test_manager_shutdown_called_on_exception(self) -> None:
        """Test that Manager.shutdown() is called even when exception occurs

        This test FAILS on base commit (no shutdown)
        This test PASSES after solution (shutdown in finally ensures cleanup)
        """

        async def run_test() -> None:
            with patch("black.concurrency.Manager") as mock_manager_class:
                # Setup mock Manager
                mock_manager = MagicMock()
                mock_lock = MagicMock()
                mock_manager.Lock.return_value = mock_lock
                mock_manager_class.return_value = mock_manager

                # Create mock executor
                loop = asyncio.get_event_loop()
                mock_executor = MagicMock()

                # Mock the executor to return a future
                from concurrent.futures import Future

                future = Future()
                future.set_result(False)
                mock_executor.submit.return_value = future

                # Mock asyncio.wait to raise an exception
                with patch(
                    "black.concurrency.asyncio.wait",
                    side_effect=RuntimeError("Test exception"),
                ):
                    with patch("black.concurrency.Cache.read", return_value=None):
                        with pytest.raises(RuntimeError):
                            await schedule_formatting(
                                sources={Path("test.py")},  # Actual source
                                fast=False,
                                write_back=WriteBack.COLOR_DIFF,
                                mode=Mode(),
                                report=Report(),
                                loop=loop,
                                executor=mock_executor,
                                no_cache=True,
                            )

                # CRITICAL: Manager.shutdown() must be called after exception
                # This FAILS on base commit (no cleanup on exception)
                # This PASSES after solution (finally ensures cleanup)
                mock_manager.shutdown.assert_called_once()

        run_async(run_test())

    def test_no_manager_created_for_non_diff_writeback(self) -> None:
        """Test that Manager is not created when not using DIFF writeback

        This documents that Manager is only needed for DIFF output
        """

        async def run_test() -> None:
            with patch('black.concurrency.Manager') as mock_manager_class:
                loop = asyncio.get_event_loop()
                mock_executor = MagicMock()

                # Call with WriteBack.YES (not DIFF, so no Manager needed)
                with patch("black.concurrency.Cache.read", return_value=None):
                    await schedule_formatting(
                        sources=set(),  # Empty sources
                        fast=False,
                        write_back=WriteBack.YES,  # Not DIFF or COLOR_DIFF
                        mode=Mode(),
                        report=Report(),
                        loop=loop,
                        executor=mock_executor,
                        no_cache=True
                    )

                # ASSERTION: Manager should NOT be created for non-DIFF writeback
                mock_manager_class.assert_not_called()

        run_async(run_test())

    def test_manager_shutdown_with_early_return(self) -> None:
        """Test that Manager is not created on early return.

        Tests the early return path when no sources need formatting
        """

        async def run_test() -> None:
            with patch('black.concurrency.Manager') as mock_manager_class:
                loop = asyncio.get_event_loop()
                mock_executor = MagicMock()

                # Mock Cache to return all sources as cached
                mock_cache = MagicMock()
                mock_cache.filtered_cached.return_value = (set(), {Path("cached.py")})

                with patch(
                    "black.concurrency.Cache.read", return_value=mock_cache
                ):
                    await schedule_formatting(
                        sources={Path("cached.py")},
                        fast=False,
                        write_back=WriteBack.YES,  # Cache is checked for non-DIFF
                        mode=Mode(),
                        report=Report(),
                        loop=loop,
                        executor=mock_executor,
                        no_cache=False
                    )

                # Manager should not be created because function returns early
                mock_manager_class.assert_not_called()

        run_async(run_test())
