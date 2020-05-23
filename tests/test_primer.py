#!/usr/bin/env python3

import asyncio
import sys
import unittest
from contextlib import contextmanager
from copy import deepcopy
from io import StringIO
from os import getpid
from pathlib import Path
from platform import system
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory, gettempdir
from typing import Any, Callable, Generator, Iterator, Tuple
from unittest.mock import Mock, patch

from click.testing import CliRunner

from black_primer import cli, lib


EXPECTED_ANALYSIS_OUTPUT = """\
-- primer results 📊 --

68 / 69 succeeded (98.55%) ✅
1 / 69 FAILED (1.45%) 💩
 - 0 projects disabled by config
 - 0 projects skipped due to Python version
 - 0 skipped due to long checkout

Failed projects:

## black:
 - Returned 69
 - stdout:
Black didn't work

"""
FAKE_PROJECT_CONFIG = {
    "cli_arguments": ["--unittest"],
    "expect_formatting_changes": False,
    "git_clone_url": "https://github.com/psf/black.git",
}


@contextmanager
def capture_stdout(command: Callable, *args: Any, **kwargs: Any) -> Generator:
    old_stdout, sys.stdout = sys.stdout, StringIO()
    try:
        command(*args, **kwargs)
        sys.stdout.seek(0)
        yield sys.stdout.read()
    finally:
        sys.stdout = old_stdout


@contextmanager
def event_loop() -> Iterator[None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    if sys.platform == "win32":
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
    try:
        yield
    finally:
        loop.close()


async def raise_subprocess_error_1(*args: Any, **kwargs: Any) -> None:
    raise CalledProcessError(1, ["unittest", "error"], b"", b"")


async def raise_subprocess_error_123(*args: Any, **kwargs: Any) -> None:
    raise CalledProcessError(123, ["unittest", "error"], b"", b"")


async def return_false(*args: Any, **kwargs: Any) -> bool:
    return False


async def return_subproccess_output(*args: Any, **kwargs: Any) -> Tuple[bytes, bytes]:
    return (b"stdout", b"stderr")


async def return_zero(*args: Any, **kwargs: Any) -> int:
    return 0


class PrimerLibTests(unittest.TestCase):
    def test_analyze_results(self) -> None:
        fake_results = lib.Results(
            {
                "disabled": 0,
                "failed": 1,
                "skipped_long_checkout": 0,
                "success": 68,
                "wrong_py_ver": 0,
            },
            {"black": CalledProcessError(69, ["black"], b"Black didn't work", b"")},
        )
        with capture_stdout(lib.analyze_results, 69, fake_results) as analyze_stdout:
            self.assertEqual(EXPECTED_ANALYSIS_OUTPUT, analyze_stdout)

    @event_loop()
    def test_black_run(self) -> None:
        """Pretend to run Black to ensure we cater for all scenarios"""
        loop = asyncio.get_event_loop()
        repo_path = Path(gettempdir())
        project_config = deepcopy(FAKE_PROJECT_CONFIG)
        results = lib.Results({"failed": 0, "success": 0}, {})

        # Test a successful Black run
        with patch("black_primer.lib._gen_check_output", return_subproccess_output):
            loop.run_until_complete(lib.black_run(repo_path, project_config, results))
        self.assertEqual(1, results.stats["success"])
        self.assertFalse(results.failed_projects)

        # Test a fail based on expecting formatting changes but not getting any
        project_config["expect_formatting_changes"] = True
        results = lib.Results({"failed": 0, "success": 0}, {})
        with patch("black_primer.lib._gen_check_output", return_subproccess_output):
            loop.run_until_complete(lib.black_run(repo_path, project_config, results))
        self.assertEqual(1, results.stats["failed"])
        self.assertTrue(results.failed_projects)

        # Test a fail based on returning 1 and not expecting formatting changes
        project_config["expect_formatting_changes"] = False
        results = lib.Results({"failed": 0, "success": 0}, {})
        with patch("black_primer.lib._gen_check_output", raise_subprocess_error_1):
            loop.run_until_complete(lib.black_run(repo_path, project_config, results))
        self.assertEqual(1, results.stats["failed"])
        self.assertTrue(results.failed_projects)

        # Test a formatting error based on returning 123
        with patch("black_primer.lib._gen_check_output", raise_subprocess_error_123):
            loop.run_until_complete(lib.black_run(repo_path, project_config, results))
        self.assertEqual(2, results.stats["failed"])

    @event_loop()
    def test_gen_check_output(self) -> None:
        loop = asyncio.get_event_loop()
        stdout, stderr = loop.run_until_complete(
            lib._gen_check_output([lib.BLACK_BINARY, "--help"])
        )
        self.assertTrue("The uncompromising code formatter" in stdout.decode("utf8"))
        self.assertEqual(None, stderr)

        # TODO: Add a test to see failure works on Windows
        if lib.WINDOWS:
            return

        false_bin = "/usr/bin/false" if system() == "Darwin" else "/bin/false"
        with self.assertRaises(CalledProcessError):
            loop.run_until_complete(lib._gen_check_output([false_bin]))

        with self.assertRaises(asyncio.TimeoutError):
            loop.run_until_complete(
                lib._gen_check_output(["/bin/sleep", "2"], timeout=0.1)
            )

    @event_loop()
    def test_git_checkout_or_rebase(self) -> None:
        loop = asyncio.get_event_loop()
        project_config = deepcopy(FAKE_PROJECT_CONFIG)
        work_path = Path(gettempdir())

        expected_repo_path = work_path / "black"
        with patch("black_primer.lib._gen_check_output", return_subproccess_output):
            returned_repo_path = loop.run_until_complete(
                lib.git_checkout_or_rebase(work_path, project_config)
            )
        self.assertEqual(expected_repo_path, returned_repo_path)

    @patch("sys.stdout", new_callable=StringIO)
    @event_loop()
    def test_process_queue(self, mock_stdout: Mock) -> None:
        loop = asyncio.get_event_loop()
        config_path = Path(lib.__file__).parent / "primer.json"
        with patch("black_primer.lib.git_checkout_or_rebase", return_false):
            with TemporaryDirectory() as td:
                return_val = loop.run_until_complete(
                    lib.process_queue(str(config_path), td, 2)
                )
                self.assertEqual(0, return_val)


class PrimerCLITests(unittest.TestCase):
    @event_loop()
    def test_async_main(self) -> None:
        loop = asyncio.get_event_loop()
        work_dir = Path(gettempdir()) / f"primer_ut_{getpid()}"
        args = {
            "config": "/config",
            "debug": False,
            "keep": False,
            "long_checkouts": False,
            "rebase": False,
            "workdir": str(work_dir),
            "workers": 69,
        }
        with patch("black_primer.cli.lib.process_queue", return_zero):
            return_val = loop.run_until_complete(cli.async_main(**args))
            self.assertEqual(0, return_val)

    def test_handle_debug(self) -> None:
        self.assertTrue(cli._handle_debug(None, None, True))

    def test_help_output(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli.main, ["--help"])
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
