#!/usr/bin/env python3
import multiprocessing
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
import inspect
from io import BytesIO
import os
from pathlib import Path
from platform import system
import regex as re
import sys
from tempfile import TemporaryDirectory
import types
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Iterator,
    TypeVar,
)
import pytest
import unittest
from unittest.mock import patch, MagicMock

import click
from click import unstyle
from click.testing import CliRunner

import black
from black import Feature, TargetVersion
from black.cache import get_cache_file
from black.debug import DebugVisitor
from black.output import diff, color_diff
from black.report import Report
import black.files

from pathspec import PathSpec

# Import other test classes
from tests.util import (
    THIS_DIR,
    read_data,
    DETERMINISTIC_HEADER,
    BlackBaseTestCase,
    DEFAULT_MODE,
    fs,
    ff,
    dump_to_stderr,
)


THIS_FILE = Path(__file__)
PY36_VERSIONS = {
    TargetVersion.PY36,
    TargetVersion.PY37,
    TargetVersion.PY38,
    TargetVersion.PY39,
}
PY36_ARGS = [f"--target-version={version.name.lower()}" for version in PY36_VERSIONS]
T = TypeVar("T")
R = TypeVar("R")

# Match the time output in a diff, but nothing else
DIFF_TIME = re.compile(r"\t[\d-:+\. ]+")


@contextmanager
def cache_dir(exists: bool = True) -> Iterator[Path]:
    with TemporaryDirectory() as workspace:
        cache_dir = Path(workspace)
        if not exists:
            cache_dir = cache_dir / "new"
        with patch("black.cache.CACHE_DIR", cache_dir):
            yield cache_dir


@contextmanager
def event_loop() -> Iterator[None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield

    finally:
        loop.close()


class FakeContext(click.Context):
    """A fake click Context for when calling functions that need it."""

    def __init__(self) -> None:
        self.default_map: Dict[str, Any] = {}


class FakeParameter(click.Parameter):
    """A fake click Parameter for when calling functions that need it."""

    def __init__(self) -> None:
        pass


class BlackRunner(CliRunner):
    """Make sure STDOUT and STDERR are kept separate when testing Black via its CLI."""

    def __init__(self) -> None:
        super().__init__(mix_stderr=False)


class BlackTestCase(BlackBaseTestCase):
    def invokeBlack(
        self, args: List[str], exit_code: int = 0, ignore_config: bool = True
    ) -> None:
        runner = BlackRunner()
        if ignore_config:
            args = ["--verbose", "--config", str(THIS_DIR / "empty.toml"), *args]
        result = runner.invoke(black.main, args)
        self.assertEqual(
            result.exit_code,
            exit_code,
            msg=(
                f"Failed with args: {args}\n"
                f"stdout: {result.stdout_bytes.decode()!r}\n"
                f"stderr: {result.stderr_bytes.decode()!r}\n"
                f"exception: {result.exception}"
            ),
        )

    @patch("black.dump_to_file", dump_to_stderr)
    def test_empty(self) -> None:
        source = expected = ""
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)

    def test_empty_ff(self) -> None:
        expected = ""
        tmp_file = Path(black.dump_to_file())
        try:
            self.assertFalse(ff(tmp_file, write_back=black.WriteBack.YES))
            with open(tmp_file, encoding="utf8") as f:
                actual = f.read()
        finally:
            os.unlink(tmp_file)
        self.assertFormatEqual(expected, actual)

    def test_piping(self) -> None:
        source, expected = read_data("src/black/__init__", data=False)
        result = BlackRunner().invoke(
            black.main,
            ["-", "--fast", f"--line-length={black.DEFAULT_LINE_LENGTH}"],
            input=BytesIO(source.encode("utf8")),
        )
        self.assertEqual(result.exit_code, 0)
        self.assertFormatEqual(expected, result.output)
        if source != result.output:
            black.assert_equivalent(source, result.output)
            black.assert_stable(source, result.output, DEFAULT_MODE)

    def test_piping_diff(self) -> None:
        diff_header = re.compile(
            r"(STDIN|STDOUT)\t\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d\d\d\d\d\d "
            r"\+\d\d\d\d"
        )
        source, _ = read_data("expression.py")
        expected, _ = read_data("expression.diff")
        config = THIS_DIR / "data" / "empty_pyproject.toml"
        args = [
            "-",
            "--fast",
            f"--line-length={black.DEFAULT_LINE_LENGTH}",
            "--diff",
            f"--config={config}",
        ]
        result = BlackRunner().invoke(
            black.main, args, input=BytesIO(source.encode("utf8"))
        )
        self.assertEqual(result.exit_code, 0)
        actual = diff_header.sub(DETERMINISTIC_HEADER, result.output)
        actual = actual.rstrip() + "\n"  # the diff output has a trailing space
        self.assertEqual(expected, actual)

    def test_piping_diff_with_color(self) -> None:
        source, _ = read_data("expression.py")
        config = THIS_DIR / "data" / "empty_pyproject.toml"
        args = [
            "-",
            "--fast",
            f"--line-length={black.DEFAULT_LINE_LENGTH}",
            "--diff",
            "--color",
            f"--config={config}",
        ]
        result = BlackRunner().invoke(
            black.main, args, input=BytesIO(source.encode("utf8"))
        )
        actual = result.output
        # Again, the contents are checked in a different test, so only look for colors.
        self.assertIn("\033[1;37m", actual)
        self.assertIn("\033[36m", actual)
        self.assertIn("\033[32m", actual)
        self.assertIn("\033[31m", actual)
        self.assertIn("\033[0m", actual)

    @patch("black.dump_to_file", dump_to_stderr)
    def _test_wip(self) -> None:
        source, expected = read_data("wip")
        sys.settrace(tracefunc)
        mode = replace(
            DEFAULT_MODE,
            experimental_string_processing=False,
            target_versions={black.TargetVersion.PY38},
        )
        actual = fs(source, mode=mode)
        sys.settrace(None)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, black.FileMode())

    @unittest.expectedFailure
    @patch("black.dump_to_file", dump_to_stderr)
    def test_trailing_comma_optional_parens_stability1(self) -> None:
        source, _expected = read_data("trailing_comma_optional_parens1")
        actual = fs(source)
        black.assert_stable(source, actual, DEFAULT_MODE)

    @unittest.expectedFailure
    @patch("black.dump_to_file", dump_to_stderr)
    def test_trailing_comma_optional_parens_stability2(self) -> None:
        source, _expected = read_data("trailing_comma_optional_parens2")
        actual = fs(source)
        black.assert_stable(source, actual, DEFAULT_MODE)

    @unittest.expectedFailure
    @patch("black.dump_to_file", dump_to_stderr)
    def test_trailing_comma_optional_parens_stability3(self) -> None:
        source, _expected = read_data("trailing_comma_optional_parens3")
        actual = fs(source)
        black.assert_stable(source, actual, DEFAULT_MODE)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_trailing_comma_optional_parens_stability1_pass2(self) -> None:
        source, _expected = read_data("trailing_comma_optional_parens1")
        actual = fs(fs(source))  # this is what `format_file_contents` does with --safe
        black.assert_stable(source, actual, DEFAULT_MODE)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_trailing_comma_optional_parens_stability2_pass2(self) -> None:
        source, _expected = read_data("trailing_comma_optional_parens2")
        actual = fs(fs(source))  # this is what `format_file_contents` does with --safe
        black.assert_stable(source, actual, DEFAULT_MODE)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_trailing_comma_optional_parens_stability3_pass2(self) -> None:
        source, _expected = read_data("trailing_comma_optional_parens3")
        actual = fs(fs(source))  # this is what `format_file_contents` does with --safe
        black.assert_stable(source, actual, DEFAULT_MODE)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_pep_572(self) -> None:
        source, expected = read_data("pep_572")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)
        if sys.version_info >= (3, 8):
            black.assert_equivalent(source, actual)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_pep_572_remove_parens(self) -> None:
        source, expected = read_data("pep_572_remove_parens")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)
        if sys.version_info >= (3, 8):
            black.assert_equivalent(source, actual)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_pep_572_do_not_remove_parens(self) -> None:
        source, expected = read_data("pep_572_do_not_remove_parens")
        # the AST safety checks will fail, but that's expected, just make sure no
        # parentheses are touched
        actual = black.format_str(source, mode=DEFAULT_MODE)
        self.assertFormatEqual(expected, actual)

    def test_pep_572_version_detection(self) -> None:
        source, _ = read_data("pep_572")
        root = black.lib2to3_parse(source)
        features = black.get_features_used(root)
        self.assertIn(black.Feature.ASSIGNMENT_EXPRESSIONS, features)
        versions = black.detect_target_versions(root)
        self.assertIn(black.TargetVersion.PY38, versions)

    def test_expression_ff(self) -> None:
        source, expected = read_data("expression")
        tmp_file = Path(black.dump_to_file(source))
        try:
            self.assertTrue(ff(tmp_file, write_back=black.WriteBack.YES))
            with open(tmp_file, encoding="utf8") as f:
                actual = f.read()
        finally:
            os.unlink(tmp_file)
        self.assertFormatEqual(expected, actual)
        with patch("black.dump_to_file", dump_to_stderr):
            black.assert_equivalent(source, actual)
            black.assert_stable(source, actual, DEFAULT_MODE)

    def test_expression_diff(self) -> None:
        source, _ = read_data("expression.py")
        config = THIS_DIR / "data" / "empty_pyproject.toml"
        expected, _ = read_data("expression.diff")
        tmp_file = Path(black.dump_to_file(source))
        diff_header = re.compile(
            rf"{re.escape(str(tmp_file))}\t\d\d\d\d-\d\d-\d\d "
            r"\d\d:\d\d:\d\d\.\d\d\d\d\d\d \+\d\d\d\d"
        )
        try:
            result = BlackRunner().invoke(
                black.main, ["--diff", str(tmp_file), f"--config={config}"]
            )
            self.assertEqual(result.exit_code, 0)
        finally:
            os.unlink(tmp_file)
        actual = result.output
        actual = diff_header.sub(DETERMINISTIC_HEADER, actual)
        if expected != actual:
            dump = black.dump_to_file(actual)
            msg = (
                "Expected diff isn't equal to the actual. If you made changes to"
                " expression.py and this is an anticipated difference, overwrite"
                f" tests/data/expression.diff with {dump}"
            )
            self.assertEqual(expected, actual, msg)

    def test_expression_diff_with_color(self) -> None:
        source, _ = read_data("expression.py")
        config = THIS_DIR / "data" / "empty_pyproject.toml"
        expected, _ = read_data("expression.diff")
        tmp_file = Path(black.dump_to_file(source))
        try:
            result = BlackRunner().invoke(
                black.main, ["--diff", "--color", str(tmp_file), f"--config={config}"]
            )
        finally:
            os.unlink(tmp_file)
        actual = result.output
        # We check the contents of the diff in `test_expression_diff`. All
        # we need to check here is that color codes exist in the result.
        self.assertIn("\033[1;37m", actual)
        self.assertIn("\033[36m", actual)
        self.assertIn("\033[32m", actual)
        self.assertIn("\033[31m", actual)
        self.assertIn("\033[0m", actual)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_pep_570(self) -> None:
        source, expected = read_data("pep_570")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)
        if sys.version_info >= (3, 8):
            black.assert_equivalent(source, actual)

    def test_detect_pos_only_arguments(self) -> None:
        source, _ = read_data("pep_570")
        root = black.lib2to3_parse(source)
        features = black.get_features_used(root)
        self.assertIn(black.Feature.POS_ONLY_ARGUMENTS, features)
        versions = black.detect_target_versions(root)
        self.assertIn(black.TargetVersion.PY38, versions)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_string_quotes(self) -> None:
        source, expected = read_data("string_quotes")
        mode = black.Mode(experimental_string_processing=True)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode)
        mode = replace(mode, string_normalization=False)
        not_normalized = fs(source, mode=mode)
        self.assertFormatEqual(source.replace("\\\n", ""), not_normalized)
        black.assert_equivalent(source, not_normalized)
        black.assert_stable(source, not_normalized, mode=mode)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_docstring_no_string_normalization(self) -> None:
        """Like test_docstring but with string normalization off."""
        source, expected = read_data("docstring_no_string_normalization")
        mode = replace(DEFAULT_MODE, string_normalization=False)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode)

    def test_long_strings_flag_disabled(self) -> None:
        """Tests for turning off the string processing logic."""
        source, expected = read_data("long_strings_flag_disabled")
        mode = replace(DEFAULT_MODE, experimental_string_processing=False)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_stable(expected, actual, mode)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_numeric_literals(self) -> None:
        source, expected = read_data("numeric_literals")
        mode = replace(DEFAULT_MODE, target_versions=PY36_VERSIONS)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_numeric_literals_ignoring_underscores(self) -> None:
        source, expected = read_data("numeric_literals_skip_underscores")
        mode = replace(DEFAULT_MODE, target_versions=PY36_VERSIONS)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode)

    def test_skip_magic_trailing_comma(self) -> None:
        source, _ = read_data("expression.py")
        expected, _ = read_data("expression_skip_magic_trailing_comma.diff")
        tmp_file = Path(black.dump_to_file(source))
        diff_header = re.compile(
            rf"{re.escape(str(tmp_file))}\t\d\d\d\d-\d\d-\d\d "
            r"\d\d:\d\d:\d\d\.\d\d\d\d\d\d \+\d\d\d\d"
        )
        try:
            result = BlackRunner().invoke(black.main, ["-C", "--diff", str(tmp_file)])
            self.assertEqual(result.exit_code, 0)
        finally:
            os.unlink(tmp_file)
        actual = result.output
        actual = diff_header.sub(DETERMINISTIC_HEADER, actual)
        actual = actual.rstrip() + "\n"  # the diff output has a trailing space
        if expected != actual:
            dump = black.dump_to_file(actual)
            msg = (
                "Expected diff isn't equal to the actual. If you made changes to"
                " expression.py and this is an anticipated difference, overwrite"
                f" tests/data/expression_skip_magic_trailing_comma.diff with {dump}"
            )
            self.assertEqual(expected, actual, msg)

    @pytest.mark.no_python2
    def test_python2_should_fail_without_optional_install(self) -> None:
        if sys.version_info < (3, 8):
            self.skipTest(
                "Python 3.6 and 3.7 will install typed-ast to work and as such will be"
                " able to parse Python 2 syntax without explicitly specifying the"
                " python2 extra"
            )

        source = "x = 1234l"
        tmp_file = Path(black.dump_to_file(source))
        try:
            runner = BlackRunner()
            result = runner.invoke(black.main, [str(tmp_file)])
            self.assertEqual(result.exit_code, 123)
        finally:
            os.unlink(tmp_file)
        actual = (
            result.stderr_bytes.decode()
            .replace("\n", "")
            .replace("\\n", "")
            .replace("\\r", "")
            .replace("\r", "")
        )
        msg = (
            "The requested source code has invalid Python 3 syntax."
            "If you are trying to format Python 2 files please reinstall Black"
            " with the 'python2' extra: `python3 -m pip install black[python2]`."
        )
        self.assertIn(msg, actual)

    @pytest.mark.python2
    @patch("black.dump_to_file", dump_to_stderr)
    def test_python2_print_function(self) -> None:
        source, expected = read_data("python2_print_function")
        mode = replace(DEFAULT_MODE, target_versions={TargetVersion.PY27})
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, mode)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_stub(self) -> None:
        mode = replace(DEFAULT_MODE, is_pyi=True)
        source, expected = read_data("stub.pyi")
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_stable(source, actual, mode)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_async_as_identifier(self) -> None:
        source_path = (THIS_DIR / "data" / "async_as_identifier.py").resolve()
        source, expected = read_data("async_as_identifier")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        major, minor = sys.version_info[:2]
        if major < 3 or (major <= 3 and minor < 7):
            black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)
        # ensure black can parse this when the target is 3.6
        self.invokeBlack([str(source_path), "--target-version", "py36"])
        # but not on 3.7, because async/await is no longer an identifier
        self.invokeBlack([str(source_path), "--target-version", "py37"], exit_code=123)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_python37(self) -> None:
        source_path = (THIS_DIR / "data" / "python37.py").resolve()
        source, expected = read_data("python37")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        major, minor = sys.version_info[:2]
        if major > 3 or (major == 3 and minor >= 7):
            black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)
        # ensure black can parse this when the target is 3.7
        self.invokeBlack([str(source_path), "--target-version", "py37"])
        # but not on 3.6, because we use async as a reserved keyword
        self.invokeBlack([str(source_path), "--target-version", "py36"], exit_code=123)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_python38(self) -> None:
        source, expected = read_data("python38")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        major, minor = sys.version_info[:2]
        if major > 3 or (major == 3 and minor >= 8):
            black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_python39(self) -> None:
        source, expected = read_data("python39")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        major, minor = sys.version_info[:2]
        if major > 3 or (major == 3 and minor >= 9):
            black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, DEFAULT_MODE)

    def test_tab_comment_indentation(self) -> None:
        contents_tab = "if 1:\n\tif 2:\n\t\tpass\n\t# comment\n\tpass\n"
        contents_spc = "if 1:\n    if 2:\n        pass\n    # comment\n    pass\n"
        self.assertFormatEqual(contents_spc, fs(contents_spc))
        self.assertFormatEqual(contents_spc, fs(contents_tab))

        contents_tab = "if 1:\n\tif 2:\n\t\tpass\n\t\t# comment\n\tpass\n"
        contents_spc = "if 1:\n    if 2:\n        pass\n        # comment\n    pass\n"
        self.assertFormatEqual(contents_spc, fs(contents_spc))
        self.assertFormatEqual(contents_spc, fs(contents_tab))

        # mixed tabs and spaces (valid Python 2 code)
        contents_tab = "if 1:\n        if 2:\n\t\tpass\n\t# comment\n        pass\n"
        contents_spc = "if 1:\n    if 2:\n        pass\n    # comment\n    pass\n"
        self.assertFormatEqual(contents_spc, fs(contents_spc))
        self.assertFormatEqual(contents_spc, fs(contents_tab))

        contents_tab = "if 1:\n        if 2:\n\t\tpass\n\t\t# comment\n        pass\n"
        contents_spc = "if 1:\n    if 2:\n        pass\n        # comment\n    pass\n"
        self.assertFormatEqual(contents_spc, fs(contents_spc))
        self.assertFormatEqual(contents_spc, fs(contents_tab))

    def test_report_verbose(self) -> None:
        report = Report(verbose=True)
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("black.output._out", out), patch("black.output._err", err):
            report.done(Path("f1"), black.Changed.NO)
            self.assertEqual(len(out_lines), 1)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], "f1 already well formatted, good job.")
            self.assertEqual(unstyle(str(report)), "1 file left unchanged.")
            self.assertEqual(report.return_code, 0)
            report.done(Path("f2"), black.Changed.YES)
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], "reformatted f2")
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 1 file left unchanged."
            )
            report.done(Path("f3"), black.Changed.CACHED)
            self.assertEqual(len(out_lines), 3)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(
                out_lines[-1], "f3 wasn't modified on disk since last run."
            )
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 2 files left unchanged."
            )
            self.assertEqual(report.return_code, 0)
            report.check = True
            self.assertEqual(report.return_code, 1)
            report.check = False
            report.failed(Path("e1"), "boom")
            self.assertEqual(len(out_lines), 3)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(err_lines[-1], "error: cannot format e1: boom")
            self.assertEqual(
                unstyle(str(report)),
                "1 file reformatted, 2 files left unchanged, 1 file failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f3"), black.Changed.YES)
            self.assertEqual(len(out_lines), 4)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(out_lines[-1], "reformatted f3")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 1 file failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.failed(Path("e2"), "boom")
            self.assertEqual(len(out_lines), 4)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(err_lines[-1], "error: cannot format e2: boom")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.path_ignored(Path("wat"), "no match")
            self.assertEqual(len(out_lines), 5)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(out_lines[-1], "wat ignored: no match")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f4"), black.Changed.NO)
            self.assertEqual(len(out_lines), 6)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(out_lines[-1], "f4 already well formatted, good job.")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 3 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.check = True
            self.assertEqual(
                unstyle(str(report)),
                "2 files would be reformatted, 3 files would be left unchanged, 2 files"
                " would fail to reformat.",
            )
            report.check = False
            report.diff = True
            self.assertEqual(
                unstyle(str(report)),
                "2 files would be reformatted, 3 files would be left unchanged, 2 files"
                " would fail to reformat.",
            )

    def test_report_quiet(self) -> None:
        report = Report(quiet=True)
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("black.output._out", out), patch("black.output._err", err):
            report.done(Path("f1"), black.Changed.NO)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(unstyle(str(report)), "1 file left unchanged.")
            self.assertEqual(report.return_code, 0)
            report.done(Path("f2"), black.Changed.YES)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 1 file left unchanged."
            )
            report.done(Path("f3"), black.Changed.CACHED)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 2 files left unchanged."
            )
            self.assertEqual(report.return_code, 0)
            report.check = True
            self.assertEqual(report.return_code, 1)
            report.check = False
            report.failed(Path("e1"), "boom")
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(err_lines[-1], "error: cannot format e1: boom")
            self.assertEqual(
                unstyle(str(report)),
                "1 file reformatted, 2 files left unchanged, 1 file failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f3"), black.Changed.YES)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 1 file failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.failed(Path("e2"), "boom")
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(err_lines[-1], "error: cannot format e2: boom")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.path_ignored(Path("wat"), "no match")
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f4"), black.Changed.NO)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 3 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.check = True
            self.assertEqual(
                unstyle(str(report)),
                "2 files would be reformatted, 3 files would be left unchanged, 2 files"
                " would fail to reformat.",
            )
            report.check = False
            report.diff = True
            self.assertEqual(
                unstyle(str(report)),
                "2 files would be reformatted, 3 files would be left unchanged, 2 files"
                " would fail to reformat.",
            )

    def test_report_normal(self) -> None:
        report = black.Report()
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("black.output._out", out), patch("black.output._err", err):
            report.done(Path("f1"), black.Changed.NO)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(unstyle(str(report)), "1 file left unchanged.")
            self.assertEqual(report.return_code, 0)
            report.done(Path("f2"), black.Changed.YES)
            self.assertEqual(len(out_lines), 1)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], "reformatted f2")
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 1 file left unchanged."
            )
            report.done(Path("f3"), black.Changed.CACHED)
            self.assertEqual(len(out_lines), 1)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], "reformatted f2")
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 2 files left unchanged."
            )
            self.assertEqual(report.return_code, 0)
            report.check = True
            self.assertEqual(report.return_code, 1)
            report.check = False
            report.failed(Path("e1"), "boom")
            self.assertEqual(len(out_lines), 1)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(err_lines[-1], "error: cannot format e1: boom")
            self.assertEqual(
                unstyle(str(report)),
                "1 file reformatted, 2 files left unchanged, 1 file failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f3"), black.Changed.YES)
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(out_lines[-1], "reformatted f3")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 1 file failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.failed(Path("e2"), "boom")
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(err_lines[-1], "error: cannot format e2: boom")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.path_ignored(Path("wat"), "no match")
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f4"), black.Changed.NO)
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 3 files left unchanged, 2 files failed to"
                " reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.check = True
            self.assertEqual(
                unstyle(str(report)),
                "2 files would be reformatted, 3 files would be left unchanged, 2 files"
                " would fail to reformat.",
            )
            report.check = False
            report.diff = True
            self.assertEqual(
                unstyle(str(report)),
                "2 files would be reformatted, 3 files would be left unchanged, 2 files"
                " would fail to reformat.",
            )

    def test_lib2to3_parse(self) -> None:
        with self.assertRaises(black.InvalidInput):
            black.lib2to3_parse("invalid syntax")

        straddling = "x + y"
        black.lib2to3_parse(straddling)
        black.lib2to3_parse(straddling, {TargetVersion.PY27})
        black.lib2to3_parse(straddling, {TargetVersion.PY36})
        black.lib2to3_parse(straddling, {TargetVersion.PY27, TargetVersion.PY36})

        py2_only = "print x"
        black.lib2to3_parse(py2_only)
        black.lib2to3_parse(py2_only, {TargetVersion.PY27})
        with self.assertRaises(black.InvalidInput):
            black.lib2to3_parse(py2_only, {TargetVersion.PY36})
        with self.assertRaises(black.InvalidInput):
            black.lib2to3_parse(py2_only, {TargetVersion.PY27, TargetVersion.PY36})

        py3_only = "exec(x, end=y)"
        black.lib2to3_parse(py3_only)
        with self.assertRaises(black.InvalidInput):
            black.lib2to3_parse(py3_only, {TargetVersion.PY27})
        black.lib2to3_parse(py3_only, {TargetVersion.PY36})
        black.lib2to3_parse(py3_only, {TargetVersion.PY27, TargetVersion.PY36})

    def test_get_features_used_decorator(self) -> None:
        # Test the feature detection of new decorator syntax
        # since this makes some test cases of test_get_features_used()
        # fails if it fails, this is tested first so that a useful case
        # is identified
        simples, relaxed = read_data("decorators")
        # skip explanation comments at the top of the file
        for simple_test in simples.split("##")[1:]:
            node = black.lib2to3_parse(simple_test)
            decorator = str(node.children[0].children[0]).strip()
            self.assertNotIn(
                Feature.RELAXED_DECORATORS,
                black.get_features_used(node),
                msg=(
                    f"decorator '{decorator}' follows python<=3.8 syntax"
                    "but is detected as 3.9+"
                    # f"The full node is\n{node!r}"
                ),
            )
        # skip the '# output' comment at the top of the output part
        for relaxed_test in relaxed.split("##")[1:]:
            node = black.lib2to3_parse(relaxed_test)
            decorator = str(node.children[0].children[0]).strip()
            self.assertIn(
                Feature.RELAXED_DECORATORS,
                black.get_features_used(node),
                msg=(
                    f"decorator '{decorator}' uses python3.9+ syntax"
                    "but is detected as python<=3.8"
                    # f"The full node is\n{node!r}"
                ),
            )

    def test_get_features_used(self) -> None:
        node = black.lib2to3_parse("def f(*, arg): ...\n")
        self.assertEqual(black.get_features_used(node), set())
        node = black.lib2to3_parse("def f(*, arg,): ...\n")
        self.assertEqual(black.get_features_used(node), {Feature.TRAILING_COMMA_IN_DEF})
        node = black.lib2to3_parse("f(*arg,)\n")
        self.assertEqual(
            black.get_features_used(node), {Feature.TRAILING_COMMA_IN_CALL}
        )
        node = black.lib2to3_parse("def f(*, arg): f'string'\n")
        self.assertEqual(black.get_features_used(node), {Feature.F_STRINGS})
        node = black.lib2to3_parse("123_456\n")
        self.assertEqual(black.get_features_used(node), {Feature.NUMERIC_UNDERSCORES})
        node = black.lib2to3_parse("123456\n")
        self.assertEqual(black.get_features_used(node), set())
        source, expected = read_data("function")
        node = black.lib2to3_parse(source)
        expected_features = {
            Feature.TRAILING_COMMA_IN_CALL,
            Feature.TRAILING_COMMA_IN_DEF,
            Feature.F_STRINGS,
        }
        self.assertEqual(black.get_features_used(node), expected_features)
        node = black.lib2to3_parse(expected)
        self.assertEqual(black.get_features_used(node), expected_features)
        source, expected = read_data("expression")
        node = black.lib2to3_parse(source)
        self.assertEqual(black.get_features_used(node), set())
        node = black.lib2to3_parse(expected)
        self.assertEqual(black.get_features_used(node), set())

    def test_get_future_imports(self) -> None:
        node = black.lib2to3_parse("\n")
        self.assertEqual(set(), black.get_future_imports(node))
        node = black.lib2to3_parse("from __future__ import black\n")
        self.assertEqual({"black"}, black.get_future_imports(node))
        node = black.lib2to3_parse("from __future__ import multiple, imports\n")
        self.assertEqual({"multiple", "imports"}, black.get_future_imports(node))
        node = black.lib2to3_parse("from __future__ import (parenthesized, imports)\n")
        self.assertEqual({"parenthesized", "imports"}, black.get_future_imports(node))
        node = black.lib2to3_parse(
            "from __future__ import multiple\nfrom __future__ import imports\n"
        )
        self.assertEqual({"multiple", "imports"}, black.get_future_imports(node))
        node = black.lib2to3_parse("# comment\nfrom __future__ import black\n")
        self.assertEqual({"black"}, black.get_future_imports(node))
        node = black.lib2to3_parse('"""docstring"""\nfrom __future__ import black\n')
        self.assertEqual({"black"}, black.get_future_imports(node))
        node = black.lib2to3_parse("some(other, code)\nfrom __future__ import black\n")
        self.assertEqual(set(), black.get_future_imports(node))
        node = black.lib2to3_parse("from some.module import black\n")
        self.assertEqual(set(), black.get_future_imports(node))
        node = black.lib2to3_parse(
            "from __future__ import unicode_literals as _unicode_literals"
        )
        self.assertEqual({"unicode_literals"}, black.get_future_imports(node))
        node = black.lib2to3_parse(
            "from __future__ import unicode_literals as _lol, print"
        )
        self.assertEqual({"unicode_literals", "print"}, black.get_future_imports(node))

    def test_debug_visitor(self) -> None:
        source, _ = read_data("debug_visitor.py")
        expected, _ = read_data("debug_visitor.out")
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("black.debug.out", out):
            DebugVisitor.show(source)
        actual = "\n".join(out_lines) + "\n"
        log_name = ""
        if expected != actual:
            log_name = black.dump_to_file(*out_lines)
        self.assertEqual(
            expected,
            actual,
            f"AST print out is different. Actual version dumped to {log_name}",
        )

    def test_format_file_contents(self) -> None:
        empty = ""
        mode = DEFAULT_MODE
        with self.assertRaises(black.NothingChanged):
            black.format_file_contents(empty, mode=mode, fast=False)
        just_nl = "\n"
        with self.assertRaises(black.NothingChanged):
            black.format_file_contents(just_nl, mode=mode, fast=False)
        same = "j = [1, 2, 3]\n"
        with self.assertRaises(black.NothingChanged):
            black.format_file_contents(same, mode=mode, fast=False)
        different = "j = [1,2,3]"
        expected = same
        actual = black.format_file_contents(different, mode=mode, fast=False)
        self.assertEqual(expected, actual)
        invalid = "return if you can"
        with self.assertRaises(black.InvalidInput) as e:
            black.format_file_contents(invalid, mode=mode, fast=False)
        self.assertEqual(str(e.exception), "Cannot parse: 1:7: return if you can")

    def test_endmarker(self) -> None:
        n = black.lib2to3_parse("\n")
        self.assertEqual(n.type, black.syms.file_input)
        self.assertEqual(len(n.children), 1)
        self.assertEqual(n.children[0].type, black.token.ENDMARKER)

    @unittest.skipIf(os.environ.get("SKIP_AST_PRINT"), "user set SKIP_AST_PRINT")
    def test_assertFormatEqual(self) -> None:
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("black.output._out", out), patch("black.output._err", err):
            with self.assertRaises(AssertionError):
                self.assertFormatEqual("j = [1, 2, 3]", "j = [1, 2, 3,]")

        out_str = "".join(out_lines)
        self.assertTrue("Expected tree:" in out_str)
        self.assertTrue("Actual tree:" in out_str)
        self.assertEqual("".join(err_lines), "")

    def test_cache_broken_file(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir() as workspace:
            cache_file = get_cache_file(mode)
            with cache_file.open("w") as fobj:
                fobj.write("this is not a pickle")
            self.assertEqual(black.read_cache(mode), {})
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            self.invokeBlack([str(src)])
            cache = black.read_cache(mode)
            self.assertIn(str(src), cache)

    def test_cache_single_file_already_cached(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            black.write_cache({}, [src], mode)
            self.invokeBlack([str(src)])
            with src.open("r") as fobj:
                self.assertEqual(fobj.read(), "print('hello')")

    @event_loop()
    def test_cache_multiple_files(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir() as workspace, patch(
            "black.ProcessPoolExecutor", new=ThreadPoolExecutor
        ):
            one = (workspace / "one.py").resolve()
            with one.open("w") as fobj:
                fobj.write("print('hello')")
            two = (workspace / "two.py").resolve()
            with two.open("w") as fobj:
                fobj.write("print('hello')")
            black.write_cache({}, [one], mode)
            self.invokeBlack([str(workspace)])
            with one.open("r") as fobj:
                self.assertEqual(fobj.read(), "print('hello')")
            with two.open("r") as fobj:
                self.assertEqual(fobj.read(), 'print("hello")\n')
            cache = black.read_cache(mode)
            self.assertIn(str(one), cache)
            self.assertIn(str(two), cache)

    def test_no_cache_when_writeback_diff(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            with patch("black.read_cache") as read_cache, patch(
                "black.write_cache"
            ) as write_cache:
                self.invokeBlack([str(src), "--diff"])
                cache_file = get_cache_file(mode)
                self.assertFalse(cache_file.exists())
                write_cache.assert_not_called()
                read_cache.assert_not_called()

    def test_no_cache_when_writeback_color_diff(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            with patch("black.read_cache") as read_cache, patch(
                "black.write_cache"
            ) as write_cache:
                self.invokeBlack([str(src), "--diff", "--color"])
                cache_file = get_cache_file(mode)
                self.assertFalse(cache_file.exists())
                write_cache.assert_not_called()
                read_cache.assert_not_called()

    @event_loop()
    def test_output_locking_when_writeback_diff(self) -> None:
        with cache_dir() as workspace:
            for tag in range(0, 4):
                src = (workspace / f"test{tag}.py").resolve()
                with src.open("w") as fobj:
                    fobj.write("print('hello')")
            with patch("black.Manager", wraps=multiprocessing.Manager) as mgr:
                self.invokeBlack(["--diff", str(workspace)], exit_code=0)
                # this isn't quite doing what we want, but if it _isn't_
                # called then we cannot be using the lock it provides
                mgr.assert_called()

    @event_loop()
    def test_output_locking_when_writeback_color_diff(self) -> None:
        with cache_dir() as workspace:
            for tag in range(0, 4):
                src = (workspace / f"test{tag}.py").resolve()
                with src.open("w") as fobj:
                    fobj.write("print('hello')")
            with patch("black.Manager", wraps=multiprocessing.Manager) as mgr:
                self.invokeBlack(["--diff", "--color", str(workspace)], exit_code=0)
                # this isn't quite doing what we want, but if it _isn't_
                # called then we cannot be using the lock it provides
                mgr.assert_called()

    def test_no_cache_when_stdin(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir():
            result = CliRunner().invoke(
                black.main, ["-"], input=BytesIO(b"print('hello')")
            )
            self.assertEqual(result.exit_code, 0)
            cache_file = get_cache_file(mode)
            self.assertFalse(cache_file.exists())

    def test_read_cache_no_cachefile(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir():
            self.assertEqual(black.read_cache(mode), {})

    def test_write_cache_read_cache(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            src.touch()
            black.write_cache({}, [src], mode)
            cache = black.read_cache(mode)
            self.assertIn(str(src), cache)
            self.assertEqual(cache[str(src)], black.get_cache_info(src))

    def test_filter_cached(self) -> None:
        with TemporaryDirectory() as workspace:
            path = Path(workspace)
            uncached = (path / "uncached").resolve()
            cached = (path / "cached").resolve()
            cached_but_changed = (path / "changed").resolve()
            uncached.touch()
            cached.touch()
            cached_but_changed.touch()
            cache = {
                str(cached): black.get_cache_info(cached),
                str(cached_but_changed): (0.0, 0),
            }
            todo, done = black.filter_cached(
                cache, {uncached, cached, cached_but_changed}
            )
            self.assertEqual(todo, {uncached, cached_but_changed})
            self.assertEqual(done, {cached})

    def test_write_cache_creates_directory_if_needed(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir(exists=False) as workspace:
            self.assertFalse(workspace.exists())
            black.write_cache({}, [], mode)
            self.assertTrue(workspace.exists())

    @event_loop()
    def test_failed_formatting_does_not_get_cached(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir() as workspace, patch(
            "black.ProcessPoolExecutor", new=ThreadPoolExecutor
        ):
            failing = (workspace / "failing.py").resolve()
            with failing.open("w") as fobj:
                fobj.write("not actually python")
            clean = (workspace / "clean.py").resolve()
            with clean.open("w") as fobj:
                fobj.write('print("hello")\n')
            self.invokeBlack([str(workspace)], exit_code=123)
            cache = black.read_cache(mode)
            self.assertNotIn(str(failing), cache)
            self.assertIn(str(clean), cache)

    def test_write_cache_write_fail(self) -> None:
        mode = DEFAULT_MODE
        with cache_dir(), patch.object(Path, "open") as mock:
            mock.side_effect = OSError
            black.write_cache({}, [], mode)

    @event_loop()
    @patch("black.ProcessPoolExecutor", MagicMock(side_effect=OSError))
    def test_works_in_mono_process_only_environment(self) -> None:
        with cache_dir() as workspace:
            for f in [
                (workspace / "one.py").resolve(),
                (workspace / "two.py").resolve(),
            ]:
                f.write_text('print("hello")\n')
            self.invokeBlack([str(workspace)])

    @event_loop()
    def test_check_diff_use_together(self) -> None:
        with cache_dir():
            # Files which will be reformatted.
            src1 = (THIS_DIR / "data" / "string_quotes.py").resolve()
            self.invokeBlack([str(src1), "--diff", "--check"], exit_code=1)
            # Files which will not be reformatted.
            src2 = (THIS_DIR / "data" / "composition.py").resolve()
            self.invokeBlack([str(src2), "--diff", "--check"])
            # Multi file command.
            self.invokeBlack([str(src1), str(src2), "--diff", "--check"], exit_code=1)

    def test_no_files(self) -> None:
        with cache_dir():
            # Without an argument, black exits with error code 0.
            self.invokeBlack([])

    def test_broken_symlink(self) -> None:
        with cache_dir() as workspace:
            symlink = workspace / "broken_link.py"
            try:
                symlink.symlink_to("nonexistent.py")
            except OSError as e:
                self.skipTest(f"Can't create symlinks: {e}")
            self.invokeBlack([str(workspace.resolve())])

    def test_read_cache_line_lengths(self) -> None:
        mode = DEFAULT_MODE
        short_mode = replace(DEFAULT_MODE, line_length=1)
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            path.touch()
            black.write_cache({}, [path], mode)
            one = black.read_cache(mode)
            self.assertIn(str(path), one)
            two = black.read_cache(short_mode)
            self.assertNotIn(str(path), two)

    def test_single_file_force_pyi(self) -> None:
        pyi_mode = replace(DEFAULT_MODE, is_pyi=True)
        contents, expected = read_data("force_pyi")
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(contents)
            self.invokeBlack([str(path), "--pyi"])
            with open(path, "r") as fh:
                actual = fh.read()
            # verify cache with --pyi is separate
            pyi_cache = black.read_cache(pyi_mode)
            self.assertIn(str(path), pyi_cache)
            normal_cache = black.read_cache(DEFAULT_MODE)
            self.assertNotIn(str(path), normal_cache)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(contents, actual)
        black.assert_stable(contents, actual, pyi_mode)

    @event_loop()
    def test_multi_file_force_pyi(self) -> None:
        reg_mode = DEFAULT_MODE
        pyi_mode = replace(DEFAULT_MODE, is_pyi=True)
        contents, expected = read_data("force_pyi")
        with cache_dir() as workspace:
            paths = [
                (workspace / "file1.py").resolve(),
                (workspace / "file2.py").resolve(),
            ]
            for path in paths:
                with open(path, "w") as fh:
                    fh.write(contents)
            self.invokeBlack([str(p) for p in paths] + ["--pyi"])
            for path in paths:
                with open(path, "r") as fh:
                    actual = fh.read()
                self.assertEqual(actual, expected)
            # verify cache with --pyi is separate
            pyi_cache = black.read_cache(pyi_mode)
            normal_cache = black.read_cache(reg_mode)
            for path in paths:
                self.assertIn(str(path), pyi_cache)
                self.assertNotIn(str(path), normal_cache)

    def test_pipe_force_pyi(self) -> None:
        source, expected = read_data("force_pyi")
        result = CliRunner().invoke(
            black.main, ["-", "-q", "--pyi"], input=BytesIO(source.encode("utf8"))
        )
        self.assertEqual(result.exit_code, 0)
        actual = result.output
        self.assertFormatEqual(actual, expected)

    def test_single_file_force_py36(self) -> None:
        reg_mode = DEFAULT_MODE
        py36_mode = replace(DEFAULT_MODE, target_versions=PY36_VERSIONS)
        source, expected = read_data("force_py36")
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(source)
            self.invokeBlack([str(path), *PY36_ARGS])
            with open(path, "r") as fh:
                actual = fh.read()
            # verify cache with --target-version is separate
            py36_cache = black.read_cache(py36_mode)
            self.assertIn(str(path), py36_cache)
            normal_cache = black.read_cache(reg_mode)
            self.assertNotIn(str(path), normal_cache)
        self.assertEqual(actual, expected)

    @event_loop()
    def test_multi_file_force_py36(self) -> None:
        reg_mode = DEFAULT_MODE
        py36_mode = replace(DEFAULT_MODE, target_versions=PY36_VERSIONS)
        source, expected = read_data("force_py36")
        with cache_dir() as workspace:
            paths = [
                (workspace / "file1.py").resolve(),
                (workspace / "file2.py").resolve(),
            ]
            for path in paths:
                with open(path, "w") as fh:
                    fh.write(source)
            self.invokeBlack([str(p) for p in paths] + PY36_ARGS)
            for path in paths:
                with open(path, "r") as fh:
                    actual = fh.read()
                self.assertEqual(actual, expected)
            # verify cache with --target-version is separate
            pyi_cache = black.read_cache(py36_mode)
            normal_cache = black.read_cache(reg_mode)
            for path in paths:
                self.assertIn(str(path), pyi_cache)
                self.assertNotIn(str(path), normal_cache)

    def test_pipe_force_py36(self) -> None:
        source, expected = read_data("force_py36")
        result = CliRunner().invoke(
            black.main,
            ["-", "-q", "--target-version=py36"],
            input=BytesIO(source.encode("utf8")),
        )
        self.assertEqual(result.exit_code, 0)
        actual = result.output
        self.assertFormatEqual(actual, expected)

    def test_include_exclude(self) -> None:
        path = THIS_DIR / "data" / "include_exclude_tests"
        include = re.compile(r"\.pyi?$")
        exclude = re.compile(r"/exclude/|/\.definitely_exclude/")
        report = black.Report()
        gitignore = PathSpec.from_lines("gitwildmatch", [])
        sources: List[Path] = []
        expected = [
            Path(path / "b/dont_exclude/a.py"),
            Path(path / "b/dont_exclude/a.pyi"),
        ]
        this_abs = THIS_DIR.resolve()
        sources.extend(
            black.gen_python_files(
                path.iterdir(),
                this_abs,
                include,
                exclude,
                None,
                None,
                report,
                gitignore,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_gitignore_used_as_default(self) -> None:
        path = Path(THIS_DIR / "data" / "include_exclude_tests")
        include = re.compile(r"\.pyi?$")
        extend_exclude = re.compile(r"/exclude/")
        src = str(path / "b/")
        report = black.Report()
        expected: List[Path] = [
            path / "b/.definitely_exclude/a.py",
            path / "b/.definitely_exclude/a.pyi",
        ]
        sources = list(
            black.get_sources(
                ctx=FakeContext(),
                src=(src,),
                quiet=True,
                verbose=False,
                include=include,
                exclude=None,
                extend_exclude=extend_exclude,
                force_exclude=None,
                report=report,
                stdin_filename=None,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    @patch("black.find_project_root", lambda *args: THIS_DIR.resolve())
    def test_exclude_for_issue_1572(self) -> None:
        # Exclude shouldn't touch files that were explicitly given to Black through the
        # CLI. Exclude is supposed to only apply to the recursive discovery of files.
        # https://github.com/psf/black/issues/1572
        path = THIS_DIR / "data" / "include_exclude_tests"
        include = ""
        exclude = r"/exclude/|a\.py"
        src = str(path / "b/exclude/a.py")
        report = black.Report()
        expected = [Path(path / "b/exclude/a.py")]
        sources = list(
            black.get_sources(
                ctx=FakeContext(),
                src=(src,),
                quiet=True,
                verbose=False,
                include=re.compile(include),
                exclude=re.compile(exclude),
                extend_exclude=None,
                force_exclude=None,
                report=report,
                stdin_filename=None,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    @patch("black.find_project_root", lambda *args: THIS_DIR.resolve())
    def test_get_sources_with_stdin(self) -> None:
        include = ""
        exclude = r"/exclude/|a\.py"
        src = "-"
        report = black.Report()
        expected = [Path("-")]
        sources = list(
            black.get_sources(
                ctx=FakeContext(),
                src=(src,),
                quiet=True,
                verbose=False,
                include=re.compile(include),
                exclude=re.compile(exclude),
                extend_exclude=None,
                force_exclude=None,
                report=report,
                stdin_filename=None,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    @patch("black.find_project_root", lambda *args: THIS_DIR.resolve())
    def test_get_sources_with_stdin_filename(self) -> None:
        include = ""
        exclude = r"/exclude/|a\.py"
        src = "-"
        report = black.Report()
        stdin_filename = str(THIS_DIR / "data/collections.py")
        expected = [Path(f"__BLACK_STDIN_FILENAME__{stdin_filename}")]
        sources = list(
            black.get_sources(
                ctx=FakeContext(),
                src=(src,),
                quiet=True,
                verbose=False,
                include=re.compile(include),
                exclude=re.compile(exclude),
                extend_exclude=None,
                force_exclude=None,
                report=report,
                stdin_filename=stdin_filename,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    @patch("black.find_project_root", lambda *args: THIS_DIR.resolve())
    def test_get_sources_with_stdin_filename_and_exclude(self) -> None:
        # Exclude shouldn't exclude stdin_filename since it is mimicking the
        # file being passed directly. This is the same as
        # test_exclude_for_issue_1572
        path = THIS_DIR / "data" / "include_exclude_tests"
        include = ""
        exclude = r"/exclude/|a\.py"
        src = "-"
        report = black.Report()
        stdin_filename = str(path / "b/exclude/a.py")
        expected = [Path(f"__BLACK_STDIN_FILENAME__{stdin_filename}")]
        sources = list(
            black.get_sources(
                ctx=FakeContext(),
                src=(src,),
                quiet=True,
                verbose=False,
                include=re.compile(include),
                exclude=re.compile(exclude),
                extend_exclude=None,
                force_exclude=None,
                report=report,
                stdin_filename=stdin_filename,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    @patch("black.find_project_root", lambda *args: THIS_DIR.resolve())
    def test_get_sources_with_stdin_filename_and_extend_exclude(self) -> None:
        # Extend exclude shouldn't exclude stdin_filename since it is mimicking the
        # file being passed directly. This is the same as
        # test_exclude_for_issue_1572
        path = THIS_DIR / "data" / "include_exclude_tests"
        include = ""
        extend_exclude = r"/exclude/|a\.py"
        src = "-"
        report = black.Report()
        stdin_filename = str(path / "b/exclude/a.py")
        expected = [Path(f"__BLACK_STDIN_FILENAME__{stdin_filename}")]
        sources = list(
            black.get_sources(
                ctx=FakeContext(),
                src=(src,),
                quiet=True,
                verbose=False,
                include=re.compile(include),
                exclude=re.compile(""),
                extend_exclude=re.compile(extend_exclude),
                force_exclude=None,
                report=report,
                stdin_filename=stdin_filename,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    @patch("black.find_project_root", lambda *args: THIS_DIR.resolve())
    def test_get_sources_with_stdin_filename_and_force_exclude(self) -> None:
        # Force exclude should exclude the file when passing it through
        # stdin_filename
        path = THIS_DIR / "data" / "include_exclude_tests"
        include = ""
        force_exclude = r"/exclude/|a\.py"
        src = "-"
        report = black.Report()
        stdin_filename = str(path / "b/exclude/a.py")
        sources = list(
            black.get_sources(
                ctx=FakeContext(),
                src=(src,),
                quiet=True,
                verbose=False,
                include=re.compile(include),
                exclude=re.compile(""),
                extend_exclude=None,
                force_exclude=re.compile(force_exclude),
                report=report,
                stdin_filename=stdin_filename,
            )
        )
        self.assertEqual([], sorted(sources))

    def test_reformat_one_with_stdin(self) -> None:
        with patch(
            "black.format_stdin_to_stdout",
            return_value=lambda *args, **kwargs: black.Changed.YES,
        ) as fsts:
            report = MagicMock()
            path = Path("-")
            black.reformat_one(
                path,
                fast=True,
                write_back=black.WriteBack.YES,
                mode=DEFAULT_MODE,
                report=report,
            )
            fsts.assert_called_once()
            report.done.assert_called_with(path, black.Changed.YES)

    def test_reformat_one_with_stdin_filename(self) -> None:
        with patch(
            "black.format_stdin_to_stdout",
            return_value=lambda *args, **kwargs: black.Changed.YES,
        ) as fsts:
            report = MagicMock()
            p = "foo.py"
            path = Path(f"__BLACK_STDIN_FILENAME__{p}")
            expected = Path(p)
            black.reformat_one(
                path,
                fast=True,
                write_back=black.WriteBack.YES,
                mode=DEFAULT_MODE,
                report=report,
            )
            fsts.assert_called_once_with(
                fast=True, write_back=black.WriteBack.YES, mode=DEFAULT_MODE
            )
            # __BLACK_STDIN_FILENAME__ should have been stripped
            report.done.assert_called_with(expected, black.Changed.YES)

    def test_reformat_one_with_stdin_filename_pyi(self) -> None:
        with patch(
            "black.format_stdin_to_stdout",
            return_value=lambda *args, **kwargs: black.Changed.YES,
        ) as fsts:
            report = MagicMock()
            p = "foo.pyi"
            path = Path(f"__BLACK_STDIN_FILENAME__{p}")
            expected = Path(p)
            black.reformat_one(
                path,
                fast=True,
                write_back=black.WriteBack.YES,
                mode=DEFAULT_MODE,
                report=report,
            )
            fsts.assert_called_once_with(
                fast=True,
                write_back=black.WriteBack.YES,
                mode=replace(DEFAULT_MODE, is_pyi=True),
            )
            # __BLACK_STDIN_FILENAME__ should have been stripped
            report.done.assert_called_with(expected, black.Changed.YES)

    def test_reformat_one_with_stdin_and_existing_path(self) -> None:
        with patch(
            "black.format_stdin_to_stdout",
            return_value=lambda *args, **kwargs: black.Changed.YES,
        ) as fsts:
            report = MagicMock()
            # Even with an existing file, since we are forcing stdin, black
            # should output to stdout and not modify the file inplace
            p = Path(str(THIS_DIR / "data/collections.py"))
            # Make sure is_file actually returns True
            self.assertTrue(p.is_file())
            path = Path(f"__BLACK_STDIN_FILENAME__{p}")
            expected = Path(p)
            black.reformat_one(
                path,
                fast=True,
                write_back=black.WriteBack.YES,
                mode=DEFAULT_MODE,
                report=report,
            )
            fsts.assert_called_once()
            # __BLACK_STDIN_FILENAME__ should have been stripped
            report.done.assert_called_with(expected, black.Changed.YES)

    def test_gitignore_exclude(self) -> None:
        path = THIS_DIR / "data" / "include_exclude_tests"
        include = re.compile(r"\.pyi?$")
        exclude = re.compile(r"")
        report = black.Report()
        gitignore = PathSpec.from_lines(
            "gitwildmatch", ["exclude/", ".definitely_exclude"]
        )
        sources: List[Path] = []
        expected = [
            Path(path / "b/dont_exclude/a.py"),
            Path(path / "b/dont_exclude/a.pyi"),
        ]
        this_abs = THIS_DIR.resolve()
        sources.extend(
            black.gen_python_files(
                path.iterdir(),
                this_abs,
                include,
                exclude,
                None,
                None,
                report,
                gitignore,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_nested_gitignore(self) -> None:
        path = Path(THIS_DIR / "data" / "nested_gitignore_tests")
        include = re.compile(r"\.pyi?$")
        exclude = re.compile(r"")
        root_gitignore = black.files.get_gitignore(path)
        report = black.Report()
        expected: List[Path] = [
            Path(path / "x.py"),
            Path(path / "root/b.py"),
            Path(path / "root/c.py"),
            Path(path / "root/child/c.py"),
        ]
        this_abs = THIS_DIR.resolve()
        sources = list(
            black.gen_python_files(
                path.iterdir(),
                this_abs,
                include,
                exclude,
                None,
                None,
                report,
                root_gitignore,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_empty_include(self) -> None:
        path = THIS_DIR / "data" / "include_exclude_tests"
        report = black.Report()
        gitignore = PathSpec.from_lines("gitwildmatch", [])
        empty = re.compile(r"")
        sources: List[Path] = []
        expected = [
            Path(path / "b/exclude/a.pie"),
            Path(path / "b/exclude/a.py"),
            Path(path / "b/exclude/a.pyi"),
            Path(path / "b/dont_exclude/a.pie"),
            Path(path / "b/dont_exclude/a.py"),
            Path(path / "b/dont_exclude/a.pyi"),
            Path(path / "b/.definitely_exclude/a.pie"),
            Path(path / "b/.definitely_exclude/a.py"),
            Path(path / "b/.definitely_exclude/a.pyi"),
            Path(path / ".gitignore"),
            Path(path / "pyproject.toml"),
        ]
        this_abs = THIS_DIR.resolve()
        sources.extend(
            black.gen_python_files(
                path.iterdir(),
                this_abs,
                empty,
                re.compile(black.DEFAULT_EXCLUDES),
                None,
                None,
                report,
                gitignore,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_extend_exclude(self) -> None:
        path = THIS_DIR / "data" / "include_exclude_tests"
        report = black.Report()
        gitignore = PathSpec.from_lines("gitwildmatch", [])
        sources: List[Path] = []
        expected = [
            Path(path / "b/exclude/a.py"),
            Path(path / "b/dont_exclude/a.py"),
        ]
        this_abs = THIS_DIR.resolve()
        sources.extend(
            black.gen_python_files(
                path.iterdir(),
                this_abs,
                re.compile(black.DEFAULT_INCLUDES),
                re.compile(r"\.pyi$"),
                re.compile(r"\.definitely_exclude"),
                None,
                report,
                gitignore,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_invalid_cli_regex(self) -> None:
        for option in ["--include", "--exclude", "--extend-exclude", "--force-exclude"]:
            self.invokeBlack(["-", option, "**()(!!*)"], exit_code=2)

    def test_required_version_matches_version(self) -> None:
        self.invokeBlack(
            ["--required-version", black.__version__], exit_code=0, ignore_config=True
        )

    def test_required_version_does_not_match_version(self) -> None:
        self.invokeBlack(
            ["--required-version", "20.99b"], exit_code=1, ignore_config=True
        )

    def test_preserves_line_endings(self) -> None:
        with TemporaryDirectory() as workspace:
            test_file = Path(workspace) / "test.py"
            for nl in ["\n", "\r\n"]:
                contents = nl.join(["def f(  ):", "    pass"])
                test_file.write_bytes(contents.encode())
                ff(test_file, write_back=black.WriteBack.YES)
                updated_contents: bytes = test_file.read_bytes()
                self.assertIn(nl.encode(), updated_contents)
                if nl == "\n":
                    self.assertNotIn(b"\r\n", updated_contents)

    def test_preserves_line_endings_via_stdin(self) -> None:
        for nl in ["\n", "\r\n"]:
            contents = nl.join(["def f(  ):", "    pass"])
            runner = BlackRunner()
            result = runner.invoke(
                black.main, ["-", "--fast"], input=BytesIO(contents.encode("utf8"))
            )
            self.assertEqual(result.exit_code, 0)
            output = result.stdout_bytes
            self.assertIn(nl.encode("utf8"), output)
            if nl == "\n":
                self.assertNotIn(b"\r\n", output)

    def test_assert_equivalent_different_asts(self) -> None:
        with self.assertRaises(AssertionError):
            black.assert_equivalent("{}", "None")

    def test_symlink_out_of_root_directory(self) -> None:
        path = MagicMock()
        root = THIS_DIR.resolve()
        child = MagicMock()
        include = re.compile(black.DEFAULT_INCLUDES)
        exclude = re.compile(black.DEFAULT_EXCLUDES)
        report = black.Report()
        gitignore = PathSpec.from_lines("gitwildmatch", [])
        # `child` should behave like a symlink which resolved path is clearly
        # outside of the `root` directory.
        path.iterdir.return_value = [child]
        child.resolve.return_value = Path("/a/b/c")
        child.as_posix.return_value = "/a/b/c"
        child.is_symlink.return_value = True
        try:
            list(
                black.gen_python_files(
                    path.iterdir(),
                    root,
                    include,
                    exclude,
                    None,
                    None,
                    report,
                    gitignore,
                )
            )
        except ValueError as ve:
            self.fail(f"`get_python_files_in_dir()` failed: {ve}")
        path.iterdir.assert_called_once()
        child.resolve.assert_called_once()
        child.is_symlink.assert_called_once()
        # `child` should behave like a strange file which resolved path is clearly
        # outside of the `root` directory.
        child.is_symlink.return_value = False
        with self.assertRaises(ValueError):
            list(
                black.gen_python_files(
                    path.iterdir(),
                    root,
                    include,
                    exclude,
                    None,
                    None,
                    report,
                    gitignore,
                )
            )
        path.iterdir.assert_called()
        self.assertEqual(path.iterdir.call_count, 2)
        child.resolve.assert_called()
        self.assertEqual(child.resolve.call_count, 2)
        child.is_symlink.assert_called()
        self.assertEqual(child.is_symlink.call_count, 2)

    def test_shhh_click(self) -> None:
        try:
            from click import _unicodefun  # type: ignore
        except ModuleNotFoundError:
            self.skipTest("Incompatible Click version")
        if not hasattr(_unicodefun, "_verify_python3_env"):
            self.skipTest("Incompatible Click version")
        # First, let's see if Click is crashing with a preferred ASCII charset.
        with patch("locale.getpreferredencoding") as gpe:
            gpe.return_value = "ASCII"
            with self.assertRaises(RuntimeError):
                _unicodefun._verify_python3_env()
        # Now, let's silence Click...
        black.patch_click()
        # ...and confirm it's silent.
        with patch("locale.getpreferredencoding") as gpe:
            gpe.return_value = "ASCII"
            try:
                _unicodefun._verify_python3_env()
            except RuntimeError as re:
                self.fail(f"`patch_click()` failed, exception still raised: {re}")

    def test_root_logger_not_used_directly(self) -> None:
        def fail(*args: Any, **kwargs: Any) -> None:
            self.fail("Record created with root logger")

        with patch.multiple(
            logging.root,
            debug=fail,
            info=fail,
            warning=fail,
            error=fail,
            critical=fail,
            log=fail,
        ):
            ff(THIS_DIR / "util.py")

    def test_invalid_config_return_code(self) -> None:
        tmp_file = Path(black.dump_to_file())
        try:
            tmp_config = Path(black.dump_to_file())
            tmp_config.unlink()
            args = ["--config", str(tmp_config), str(tmp_file)]
            self.invokeBlack(args, exit_code=2, ignore_config=False)
        finally:
            tmp_file.unlink()

    def test_parse_pyproject_toml(self) -> None:
        test_toml_file = THIS_DIR / "test.toml"
        config = black.parse_pyproject_toml(str(test_toml_file))
        self.assertEqual(config["verbose"], 1)
        self.assertEqual(config["check"], "no")
        self.assertEqual(config["diff"], "y")
        self.assertEqual(config["color"], True)
        self.assertEqual(config["line_length"], 79)
        self.assertEqual(config["target_version"], ["py36", "py37", "py38"])
        self.assertEqual(config["exclude"], r"\.pyi?$")
        self.assertEqual(config["include"], r"\.py?$")

    def test_read_pyproject_toml(self) -> None:
        test_toml_file = THIS_DIR / "test.toml"
        fake_ctx = FakeContext()
        black.read_pyproject_toml(fake_ctx, FakeParameter(), str(test_toml_file))
        config = fake_ctx.default_map
        self.assertEqual(config["verbose"], "1")
        self.assertEqual(config["check"], "no")
        self.assertEqual(config["diff"], "y")
        self.assertEqual(config["color"], "True")
        self.assertEqual(config["line_length"], "79")
        self.assertEqual(config["target_version"], ["py36", "py37", "py38"])
        self.assertEqual(config["exclude"], r"\.pyi?$")
        self.assertEqual(config["include"], r"\.py?$")

    def test_find_project_root(self) -> None:
        with TemporaryDirectory() as workspace:
            root = Path(workspace)
            test_dir = root / "test"
            test_dir.mkdir()

            src_dir = root / "src"
            src_dir.mkdir()

            root_pyproject = root / "pyproject.toml"
            root_pyproject.touch()
            src_pyproject = src_dir / "pyproject.toml"
            src_pyproject.touch()
            src_python = src_dir / "foo.py"
            src_python.touch()

            self.assertEqual(
                black.find_project_root((src_dir, test_dir)), root.resolve()
            )
            self.assertEqual(black.find_project_root((src_dir,)), src_dir.resolve())
            self.assertEqual(black.find_project_root((src_python,)), src_dir.resolve())

    @patch(
        "black.files.find_user_pyproject_toml",
        black.files.find_user_pyproject_toml.__wrapped__,
    )
    def test_find_user_pyproject_toml_linux(self) -> None:
        if system() == "Windows":
            return

        # Test if XDG_CONFIG_HOME is checked
        with TemporaryDirectory() as workspace:
            tmp_user_config = Path(workspace) / "black"
            with patch.dict("os.environ", {"XDG_CONFIG_HOME": workspace}):
                self.assertEqual(
                    black.files.find_user_pyproject_toml(), tmp_user_config.resolve()
                )

        # Test fallback for XDG_CONFIG_HOME
        with patch.dict("os.environ"):
            os.environ.pop("XDG_CONFIG_HOME", None)
            fallback_user_config = Path("~/.config").expanduser() / "black"
            self.assertEqual(
                black.files.find_user_pyproject_toml(), fallback_user_config.resolve()
            )

    def test_find_user_pyproject_toml_windows(self) -> None:
        if system() != "Windows":
            return

        user_config_path = Path.home() / ".black"
        self.assertEqual(
            black.files.find_user_pyproject_toml(), user_config_path.resolve()
        )

    def test_bpo_33660_workaround(self) -> None:
        if system() == "Windows":
            return

        # https://bugs.python.org/issue33660

        old_cwd = Path.cwd()
        try:
            root = Path("/")
            os.chdir(str(root))
            path = Path("workspace") / "project"
            report = black.Report(verbose=True)
            normalized_path = black.normalize_path_maybe_ignore(path, root, report)
            self.assertEqual(normalized_path, "workspace/project")
        finally:
            os.chdir(str(old_cwd))

    def test_newline_comment_interaction(self) -> None:
        source = "class A:\\\r\n# type: ignore\n pass\n"
        output = black.format_str(source, mode=DEFAULT_MODE)
        black.assert_stable(source, output, mode=DEFAULT_MODE)

    def test_bpo_2142_workaround(self) -> None:

        # https://bugs.python.org/issue2142

        source, _ = read_data("missing_final_newline.py")
        # read_data adds a trailing newline
        source = source.rstrip()
        expected, _ = read_data("missing_final_newline.diff")
        tmp_file = Path(black.dump_to_file(source, ensure_final_newline=False))
        diff_header = re.compile(
            rf"{re.escape(str(tmp_file))}\t\d\d\d\d-\d\d-\d\d "
            r"\d\d:\d\d:\d\d\.\d\d\d\d\d\d \+\d\d\d\d"
        )
        try:
            result = BlackRunner().invoke(black.main, ["--diff", str(tmp_file)])
            self.assertEqual(result.exit_code, 0)
        finally:
            os.unlink(tmp_file)
        actual = result.output
        actual = diff_header.sub(DETERMINISTIC_HEADER, actual)
        self.assertEqual(actual, expected)

    @pytest.mark.python2
    def test_docstring_reformat_for_py27(self) -> None:
        """
        Check that stripping trailing whitespace from Python 2 docstrings
        doesn't trigger a "not equivalent to source" error
        """
        source = (
            b'def foo():\r\n    """Testing\r\n    Testing """\r\n    print "Foo"\r\n'
        )
        expected = 'def foo():\n    """Testing\n    Testing"""\n    print "Foo"\n'

        result = CliRunner().invoke(
            black.main,
            ["-", "-q", "--target-version=py27"],
            input=BytesIO(source),
        )

        self.assertEqual(result.exit_code, 0)
        actual = result.output
        self.assertFormatEqual(actual, expected)

    @staticmethod
    def compare_results(
        result: click.testing.Result, expected_value: str, expected_exit_code: int
    ) -> None:
        """Helper method to test the value and exit code of a click Result."""
        assert (
            result.output == expected_value
        ), "The output did not match the expected value."
        assert result.exit_code == expected_exit_code, "The exit code is incorrect."

    def test_code_option(self) -> None:
        """Test the code option with no changes."""
        code = 'print("Hello world")\n'
        args = ["--code", code]
        result = CliRunner().invoke(black.main, args)

        self.compare_results(result, code, 0)

    def test_code_option_changed(self) -> None:
        """Test the code option when changes are required."""
        code = "print('hello world')"
        formatted = black.format_str(code, mode=DEFAULT_MODE)

        args = ["--code", code]
        result = CliRunner().invoke(black.main, args)

        self.compare_results(result, formatted, 0)

    def test_code_option_check(self) -> None:
        """Test the code option when check is passed."""
        args = ["--check", "--code", 'print("Hello world")\n']
        result = CliRunner().invoke(black.main, args)
        self.compare_results(result, "", 0)

    def test_code_option_check_changed(self) -> None:
        """Test the code option when changes are required, and check is passed."""
        args = ["--check", "--code", "print('hello world')"]
        result = CliRunner().invoke(black.main, args)
        self.compare_results(result, "", 1)

    def test_code_option_diff(self) -> None:
        """Test the code option when diff is passed."""
        code = "print('hello world')"
        formatted = black.format_str(code, mode=DEFAULT_MODE)
        result_diff = diff(code, formatted, "STDIN", "STDOUT")

        args = ["--diff", "--code", code]
        result = CliRunner().invoke(black.main, args)

        # Remove time from diff
        output = DIFF_TIME.sub("", result.output)

        assert output == result_diff, "The output did not match the expected value."
        assert result.exit_code == 0, "The exit code is incorrect."

    def test_code_option_color_diff(self) -> None:
        """Test the code option when color and diff are passed."""
        code = "print('hello world')"
        formatted = black.format_str(code, mode=DEFAULT_MODE)

        result_diff = diff(code, formatted, "STDIN", "STDOUT")
        result_diff = color_diff(result_diff)

        args = ["--diff", "--color", "--code", code]
        result = CliRunner().invoke(black.main, args)

        # Remove time from diff
        output = DIFF_TIME.sub("", result.output)

        assert output == result_diff, "The output did not match the expected value."
        assert result.exit_code == 0, "The exit code is incorrect."

    def test_code_option_safe(self) -> None:
        """Test that the code option throws an error when the sanity checks fail."""
        # Patch black.assert_equivalent to ensure the sanity checks fail
        with patch.object(black, "assert_equivalent", side_effect=AssertionError):
            code = 'print("Hello world")'
            error_msg = f"{code}\nerror: cannot format <string>: \n"

            args = ["--safe", "--code", code]
            result = CliRunner().invoke(black.main, args)

            self.compare_results(result, error_msg, 123)

    def test_code_option_fast(self) -> None:
        """Test that the code option ignores errors when the sanity checks fail."""
        # Patch black.assert_equivalent to ensure the sanity checks fail
        with patch.object(black, "assert_equivalent", side_effect=AssertionError):
            code = 'print("Hello world")'
            formatted = black.format_str(code, mode=DEFAULT_MODE)

            args = ["--fast", "--code", code]
            result = CliRunner().invoke(black.main, args)

            self.compare_results(result, formatted, 0)

    def test_code_option_config(self) -> None:
        """
        Test that the code option finds the pyproject.toml in the current directory.
        """
        with patch.object(black, "parse_pyproject_toml", return_value={}) as parse:
            # Make sure we are in the project root with the pyproject file
            if not Path("tests").exists():
                os.chdir("..")

            args = ["--code", "print"]
            CliRunner().invoke(black.main, args)

            pyproject_path = Path(Path().cwd(), "pyproject.toml").resolve()
            assert (
                len(parse.mock_calls) >= 1
            ), "Expected config parse to be called with the current directory."

            _, call_args, _ = parse.mock_calls[0]
            assert (
                call_args[0].lower() == str(pyproject_path).lower()
            ), "Incorrect config loaded."

    def test_code_option_parent_config(self) -> None:
        """
        Test that the code option finds the pyproject.toml in the parent directory.
        """
        with patch.object(black, "parse_pyproject_toml", return_value={}) as parse:
            # Make sure we are in the tests directory
            if Path("tests").exists():
                os.chdir("tests")

            args = ["--code", "print"]
            CliRunner().invoke(black.main, args)

            pyproject_path = Path(Path().cwd().parent, "pyproject.toml").resolve()
            assert (
                len(parse.mock_calls) >= 1
            ), "Expected config parse to be called with the current directory."

            _, call_args, _ = parse.mock_calls[0]
            assert (
                call_args[0].lower() == str(pyproject_path).lower()
            ), "Incorrect config loaded."


with open(black.__file__, "r", encoding="utf-8") as _bf:
    black_source_lines = _bf.readlines()


def tracefunc(frame: types.FrameType, event: str, arg: Any) -> Callable:
    """Show function calls `from black/__init__.py` as they happen.

    Register this with `sys.settrace()` in a test you're debugging.
    """
    if event != "call":
        return tracefunc

    stack = len(inspect.stack()) - 19
    stack *= 2
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    func_sig_lineno = lineno - 1
    funcname = black_source_lines[func_sig_lineno].strip()
    while funcname.startswith("@"):
        func_sig_lineno += 1
        funcname = black_source_lines[func_sig_lineno].strip()
    if "black/__init__.py" in filename:
        print(f"{' ' * stack}{lineno}:{funcname}")
    return tracefunc


if __name__ == "__main__":
    unittest.main(module="test_black")
