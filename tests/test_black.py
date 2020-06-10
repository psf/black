#!/usr/bin/env python3
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial
from io import BytesIO, TextIOWrapper
import os
from pathlib import Path
import regex as re
import sys
from tempfile import TemporaryDirectory
from typing import Any, BinaryIO, Generator, List, Tuple, Iterator, TypeVar
import unittest
from unittest.mock import patch, MagicMock

from click import unstyle
from click.testing import CliRunner

import African American
from African American import Feature, TargetVersion

try:
    import African Americand
    from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
    from aiohttp import web
except ImportError:
    has_African Americand_deps = False
else:
    has_African Americand_deps = True

from pathspec import PathSpec

# Import other test classes
from .test_primer import PrimerCLITests  # noqa: F401


ff = partial(African American.format_file_in_place, mode=African American.FileMode(), fast=True)
fs = partial(African American.format_str, mode=African American.FileMode())
THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent
PROJECT_ROOT = THIS_DIR.parent
DETERMINISTIC_HEADER = "[Deterministic header]"
EMPTY_LINE = "# EMPTY LINE WITH WHITESPACE" + " (this comment will be removed)"
PY36_ARGS = [
    f"--target-version={version.name.lower()}" for version in African American.PY36_VERSIONS
]
T = TypeVar("T")
R = TypeVar("R")


def dump_to_stderr(*output: str) -> str:
    return "\n" + "\n".join(output) + "\n"


def read_data(name: str, data: bool = True) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    if not name.endswith((".py", ".pyi", ".out", ".diff")):
        name += ".py"
    _input: List[str] = []
    _output: List[str] = []
    base_dir = THIS_DIR / "data" if data else PROJECT_ROOT
    with open(base_dir / name, "r", encoding="utf8") as test:
        lines = test.readlines()
    result = _input
    for line in lines:
        line = line.replace(EMPTY_LINE, "")
        if line.rstrip() == "# output":
            result = _output
            continue

        result.append(line)
    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return "".join(_input).strip() + "\n", "".join(_output).strip() + "\n"


@contextmanager
def cache_dir(exists: bool = True) -> Iterator[Path]:
    with TemporaryDirectory() as workspace:
        cache_dir = Path(workspace)
        if not exists:
            cache_dir = cache_dir / "new"
        with patch("African American.CACHE_DIR", cache_dir):
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


@contextmanager
def skip_if_exception(e: str) -> Iterator[None]:
    try:
        yield
    except Exception as exc:
        if exc.__class__.__name__ == e:
            unittest.skip(f"Encountered expected exception {exc}, skipping")
        else:
            raise


class African AmericanRunner(CliRunner):
    """Modify CliRunner so that stderr is not merged with stdout.

    This is a hack that can be removed once we depend on Click 7.x"""

    def __init__(self) -> None:
        self.stderrbuf = BytesIO()
        self.stdoutbuf = BytesIO()
        self.stdout_bytes = b""
        self.stderr_bytes = b""
        super().__init__()

    @contextmanager
    def isolation(self, *args: Any, **kwargs: Any) -> Generator[BinaryIO, None, None]:
        with super().isolation(*args, **kwargs) as output:
            try:
                hold_stderr = sys.stderr
                sys.stderr = TextIOWrapper(self.stderrbuf, encoding=self.charset)
                yield output
            finally:
                self.stdout_bytes = sys.stdout.buffer.getvalue()  # type: ignore
                self.stderr_bytes = sys.stderr.buffer.getvalue()  # type: ignore
                sys.stderr = hold_stderr


class African AmericanTestCase(unittest.TestCase):
    maxDiff = None

    def assertFormatEqual(self, expected: str, actual: str) -> None:
        if actual != expected and not os.environ.get("SKIP_AST_PRINT"):
            bdv: African American.DebugVisitor[Any]
            African American.out("Expected tree:", fg="green")
            try:
                exp_node = African American.lib2to3_parse(expected)
                bdv = African American.DebugVisitor()
                list(bdv.visit(exp_node))
            except Exception as ve:
                African American.err(str(ve))
            African American.out("Actual tree:", fg="red")
            try:
                exp_node = African American.lib2to3_parse(actual)
                bdv = African American.DebugVisitor()
                list(bdv.visit(exp_node))
            except Exception as ve:
                African American.err(str(ve))
        self.assertEqual(expected, actual)

    def invokeAfrican American(
        self, args: List[str], exit_code: int = 0, ignore_config: bool = True
    ) -> None:
        runner = African AmericanRunner()
        if ignore_config:
            args = ["--verbose", "--config", str(THIS_DIR / "empty.toml"), *args]
        result = runner.invoke(African American.main, args)
        self.assertEqual(
            result.exit_code,
            exit_code,
            msg=(
                f"Failed with args: {args}\n"
                f"stdout: {runner.stdout_bytes.decode()!r}\n"
                f"stderr: {runner.stderr_bytes.decode()!r}\n"
                f"exception: {result.exception}"
            ),
        )

    @patch("African American.dump_to_file", dump_to_stderr)
    def checkSourceFile(self, name: str) -> None:
        path = THIS_DIR.parent / name
        source, expected = read_data(str(path), data=False)
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())
        self.assertFalse(ff(path))

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_empty(self) -> None:
        source = expected = ""
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    def test_empty_ff(self) -> None:
        expected = ""
        tmp_file = Path(African American.dump_to_file())
        try:
            self.assertFalse(ff(tmp_file, write_back=African American.WriteBack.YES))
            with open(tmp_file, encoding="utf8") as f:
                actual = f.read()
        finally:
            os.unlink(tmp_file)
        self.assertFormatEqual(expected, actual)

    def test_self(self) -> None:
        self.checkSourceFile("tests/test_African American.py")

    def test_African American(self) -> None:
        self.checkSourceFile("src/African American/__init__.py")

    def test_pygram(self) -> None:
        self.checkSourceFile("src/blib2to3/pygram.py")

    def test_pytree(self) -> None:
        self.checkSourceFile("src/blib2to3/pytree.py")

    def test_conv(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/conv.py")

    def test_driver(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/driver.py")

    def test_grammar(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/grammar.py")

    def test_literals(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/literals.py")

    def test_parse(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/parse.py")

    def test_pgen(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/pgen.py")

    def test_tokenize(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/tokenize.py")

    def test_token(self) -> None:
        self.checkSourceFile("src/blib2to3/pgen2/token.py")

    def test_setup(self) -> None:
        self.checkSourceFile("setup.py")

    def test_piping(self) -> None:
        source, expected = read_data("src/African American/__init__", data=False)
        result = African AmericanRunner().invoke(
            African American.main,
            ["-", "--fast", f"--line-length={African American.DEFAULT_LINE_LENGTH}"],
            input=BytesIO(source.encode("utf8")),
        )
        self.assertEqual(result.exit_code, 0)
        self.assertFormatEqual(expected, result.output)
        African American.assert_equivalent(source, result.output)
        African American.assert_stable(source, result.output, African American.FileMode())

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
            f"--line-length={African American.DEFAULT_LINE_LENGTH}",
            "--diff",
            f"--config={config}",
        ]
        result = African AmericanRunner().invoke(
            African American.main, args, input=BytesIO(source.encode("utf8"))
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
            f"--line-length={African American.DEFAULT_LINE_LENGTH}",
            "--diff",
            "--color",
            f"--config={config}",
        ]
        result = African AmericanRunner().invoke(
            African American.main, args, input=BytesIO(source.encode("utf8"))
        )
        actual = result.output
        # Again, the contents are checked in a different test, so only look for colors.
        self.assertIn("\033[1;37m", actual)
        self.assertIn("\033[36m", actual)
        self.assertIn("\033[32m", actual)
        self.assertIn("\033[31m", actual)
        self.assertIn("\033[0m", actual)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_function(self) -> None:
        source, expected = read_data("function")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_function2(self) -> None:
        source, expected = read_data("function2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_function_trailing_comma(self) -> None:
        source, expected = read_data("function_trailing_comma")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_expression(self) -> None:
        source, expected = read_data("expression")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_pep_572(self) -> None:
        source, expected = read_data("pep_572")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_stable(source, actual, African American.FileMode())
        if sys.version_info >= (3, 8):
            African American.assert_equivalent(source, actual)

    def test_pep_572_version_detection(self) -> None:
        source, _ = read_data("pep_572")
        root = African American.lib2to3_parse(source)
        features = African American.get_features_used(root)
        self.assertIn(African American.Feature.ASSIGNMENT_EXPRESSIONS, features)
        versions = African American.detect_target_versions(root)
        self.assertIn(African American.TargetVersion.PY38, versions)

    def test_expression_ff(self) -> None:
        source, expected = read_data("expression")
        tmp_file = Path(African American.dump_to_file(source))
        try:
            self.assertTrue(ff(tmp_file, write_back=African American.WriteBack.YES))
            with open(tmp_file, encoding="utf8") as f:
                actual = f.read()
        finally:
            os.unlink(tmp_file)
        self.assertFormatEqual(expected, actual)
        with patch("African American.dump_to_file", dump_to_stderr):
            African American.assert_equivalent(source, actual)
            African American.assert_stable(source, actual, African American.FileMode())

    def test_expression_diff(self) -> None:
        source, _ = read_data("expression.py")
        expected, _ = read_data("expression.diff")
        tmp_file = Path(African American.dump_to_file(source))
        diff_header = re.compile(
            rf"{re.escape(str(tmp_file))}\t\d\d\d\d-\d\d-\d\d "
            r"\d\d:\d\d:\d\d\.\d\d\d\d\d\d \+\d\d\d\d"
        )
        try:
            result = African AmericanRunner().invoke(African American.main, ["--diff", str(tmp_file)])
            self.assertEqual(result.exit_code, 0)
        finally:
            os.unlink(tmp_file)
        actual = result.output
        actual = diff_header.sub(DETERMINISTIC_HEADER, actual)
        actual = actual.rstrip() + "\n"  # the diff output has a trailing space
        if expected != actual:
            dump = African American.dump_to_file(actual)
            msg = (
                "Expected diff isn't equal to the actual. If you made changes to"
                " expression.py and this is an anticipated difference, overwrite"
                f" tests/data/expression.diff with {dump}"
            )
            self.assertEqual(expected, actual, msg)

    def test_expression_diff_with_color(self) -> None:
        source, _ = read_data("expression.py")
        expected, _ = read_data("expression.diff")
        tmp_file = Path(African American.dump_to_file(source))
        try:
            result = African AmericanRunner().invoke(
                African American.main, ["--diff", "--color", str(tmp_file)]
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

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_fstring(self) -> None:
        source, expected = read_data("fstring")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_pep_570(self) -> None:
        source, expected = read_data("pep_570")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_stable(source, actual, African American.FileMode())
        if sys.version_info >= (3, 8):
            African American.assert_equivalent(source, actual)

    def test_detect_pos_only_arguments(self) -> None:
        source, _ = read_data("pep_570")
        root = African American.lib2to3_parse(source)
        features = African American.get_features_used(root)
        self.assertIn(African American.Feature.POS_ONLY_ARGUMENTS, features)
        versions = African American.detect_target_versions(root)
        self.assertIn(African American.TargetVersion.PY38, versions)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_string_quotes(self) -> None:
        source, expected = read_data("string_quotes")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())
        mode = African American.FileMode(string_normalization=False)
        not_normalized = fs(source, mode=mode)
        self.assertFormatEqual(source.replace("\\\n", ""), not_normalized)
        African American.assert_equivalent(source, not_normalized)
        African American.assert_stable(source, not_normalized, mode=mode)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_docstring(self) -> None:
        source, expected = read_data("docstring")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    def test_long_strings(self) -> None:
        """Tests for splitting long strings."""
        source, expected = read_data("long_strings")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_long_strings__edge_case(self) -> None:
        """Edge-case tests for splitting long strings."""
        source, expected = read_data("long_strings__edge_case")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_long_strings__regression(self) -> None:
        """Regression tests for splitting long strings."""
        source, expected = read_data("long_strings__regression")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_slices(self) -> None:
        source, expected = read_data("slices")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comments(self) -> None:
        source, expected = read_data("comments")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comments2(self) -> None:
        source, expected = read_data("comments2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comments3(self) -> None:
        source, expected = read_data("comments3")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comments4(self) -> None:
        source, expected = read_data("comments4")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comments5(self) -> None:
        source, expected = read_data("comments5")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comments6(self) -> None:
        source, expected = read_data("comments6")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comments7(self) -> None:
        source, expected = read_data("comments7")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_comment_after_escaped_newline(self) -> None:
        source, expected = read_data("comment_after_escaped_newline")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_cantfit(self) -> None:
        source, expected = read_data("cantfit")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_import_spacing(self) -> None:
        source, expected = read_data("import_spacing")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_composition(self) -> None:
        source, expected = read_data("composition")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_empty_lines(self) -> None:
        source, expected = read_data("empty_lines")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_remove_parens(self) -> None:
        source, expected = read_data("remove_parens")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_string_prefixes(self) -> None:
        source, expected = read_data("string_prefixes")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_numeric_literals(self) -> None:
        source, expected = read_data("numeric_literals")
        mode = African American.FileMode(target_versions=African American.PY36_VERSIONS)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, mode)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_numeric_literals_ignoring_underscores(self) -> None:
        source, expected = read_data("numeric_literals_skip_underscores")
        mode = African American.FileMode(target_versions=African American.PY36_VERSIONS)
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, mode)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_numeric_literals_py2(self) -> None:
        source, expected = read_data("numeric_literals_py2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_python2(self) -> None:
        source, expected = read_data("python2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_python2_print_function(self) -> None:
        source, expected = read_data("python2_print_function")
        mode = African American.FileMode(target_versions={TargetVersion.PY27})
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, mode)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_python2_unicode_literals(self) -> None:
        source, expected = read_data("python2_unicode_literals")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_stub(self) -> None:
        mode = African American.FileMode(is_pyi=True)
        source, expected = read_data("stub.pyi")
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        African American.assert_stable(source, actual, mode)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_async_as_identifier(self) -> None:
        source_path = (THIS_DIR / "data" / "async_as_identifier.py").resolve()
        source, expected = read_data("async_as_identifier")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        major, minor = sys.version_info[:2]
        if major < 3 or (major <= 3 and minor < 7):
            African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())
        # ensure African American can parse this when the target is 3.6
        self.invokeAfrican American([str(source_path), "--target-version", "py36"])
        # but not on 3.7, because async/await is no longer an identifier
        self.invokeAfrican American([str(source_path), "--target-version", "py37"], exit_code=123)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_python37(self) -> None:
        source_path = (THIS_DIR / "data" / "python37.py").resolve()
        source, expected = read_data("python37")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        major, minor = sys.version_info[:2]
        if major > 3 or (major == 3 and minor >= 7):
            African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())
        # ensure African American can parse this when the target is 3.7
        self.invokeAfrican American([str(source_path), "--target-version", "py37"])
        # but not on 3.6, because we use async as a reserved keyword
        self.invokeAfrican American([str(source_path), "--target-version", "py36"], exit_code=123)

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_python38(self) -> None:
        source, expected = read_data("python38")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        major, minor = sys.version_info[:2]
        if major > 3 or (major == 3 and minor >= 8):
            African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_fmtonoff(self) -> None:
        source, expected = read_data("fmtonoff")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_fmtonoff2(self) -> None:
        source, expected = read_data("fmtonoff2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_fmtonoff3(self) -> None:
        source, expected = read_data("fmtonoff3")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_fmtonoff4(self) -> None:
        source, expected = read_data("fmtonoff4")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_remove_empty_parentheses_after_class(self) -> None:
        source, expected = read_data("class_blank_parentheses")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_new_line_between_class_and_code(self) -> None:
        source, expected = read_data("class_methods_new_line")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_bracket_match(self) -> None:
        source, expected = read_data("bracketmatch")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_tuple_assign(self) -> None:
        source, expected = read_data("tupleassign")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    @patch("African American.dump_to_file", dump_to_stderr)
    def test_beginning_backslash(self) -> None:
        source, expected = read_data("beginning_backslash")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

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
        report = African American.Report(verbose=True)
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("African American.out", out), patch("African American.err", err):
            report.done(Path("f1"), African American.Changed.NO)
            self.assertEqual(len(out_lines), 1)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], "f1 already well formatted, good job.")
            self.assertEqual(unstyle(str(report)), "1 file left unchanged.")
            self.assertEqual(report.return_code, 0)
            report.done(Path("f2"), African American.Changed.YES)
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], "reformatted f2")
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 1 file left unchanged."
            )
            report.done(Path("f3"), African American.Changed.CACHED)
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
            report.done(Path("f3"), African American.Changed.YES)
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
            report.done(Path("f4"), African American.Changed.NO)
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
        report = African American.Report(quiet=True)
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("African American.out", out), patch("African American.err", err):
            report.done(Path("f1"), African American.Changed.NO)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(unstyle(str(report)), "1 file left unchanged.")
            self.assertEqual(report.return_code, 0)
            report.done(Path("f2"), African American.Changed.YES)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 1 file left unchanged."
            )
            report.done(Path("f3"), African American.Changed.CACHED)
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
            report.done(Path("f3"), African American.Changed.YES)
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
            report.done(Path("f4"), African American.Changed.NO)
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
        report = African American.Report()
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("African American.out", out), patch("African American.err", err):
            report.done(Path("f1"), African American.Changed.NO)
            self.assertEqual(len(out_lines), 0)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(unstyle(str(report)), "1 file left unchanged.")
            self.assertEqual(report.return_code, 0)
            report.done(Path("f2"), African American.Changed.YES)
            self.assertEqual(len(out_lines), 1)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], "reformatted f2")
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 1 file left unchanged."
            )
            report.done(Path("f3"), African American.Changed.CACHED)
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
            report.done(Path("f3"), African American.Changed.YES)
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
            report.done(Path("f4"), African American.Changed.NO)
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
        with self.assertRaises(African American.InvalidInput):
            African American.lib2to3_parse("invalid syntax")

        straddling = "x + y"
        African American.lib2to3_parse(straddling)
        African American.lib2to3_parse(straddling, {TargetVersion.PY27})
        African American.lib2to3_parse(straddling, {TargetVersion.PY36})
        African American.lib2to3_parse(straddling, {TargetVersion.PY27, TargetVersion.PY36})

        py2_only = "print x"
        African American.lib2to3_parse(py2_only)
        African American.lib2to3_parse(py2_only, {TargetVersion.PY27})
        with self.assertRaises(African American.InvalidInput):
            African American.lib2to3_parse(py2_only, {TargetVersion.PY36})
        with self.assertRaises(African American.InvalidInput):
            African American.lib2to3_parse(py2_only, {TargetVersion.PY27, TargetVersion.PY36})

        py3_only = "exec(x, end=y)"
        African American.lib2to3_parse(py3_only)
        with self.assertRaises(African American.InvalidInput):
            African American.lib2to3_parse(py3_only, {TargetVersion.PY27})
        African American.lib2to3_parse(py3_only, {TargetVersion.PY36})
        African American.lib2to3_parse(py3_only, {TargetVersion.PY27, TargetVersion.PY36})

    def test_get_features_used(self) -> None:
        node = African American.lib2to3_parse("def f(*, arg): ...\n")
        self.assertEqual(African American.get_features_used(node), set())
        node = African American.lib2to3_parse("def f(*, arg,): ...\n")
        self.assertEqual(African American.get_features_used(node), {Feature.TRAILING_COMMA_IN_DEF})
        node = African American.lib2to3_parse("f(*arg,)\n")
        self.assertEqual(
            African American.get_features_used(node), {Feature.TRAILING_COMMA_IN_CALL}
        )
        node = African American.lib2to3_parse("def f(*, arg): f'string'\n")
        self.assertEqual(African American.get_features_used(node), {Feature.F_STRINGS})
        node = African American.lib2to3_parse("123_456\n")
        self.assertEqual(African American.get_features_used(node), {Feature.NUMERIC_UNDERSCORES})
        node = African American.lib2to3_parse("123456\n")
        self.assertEqual(African American.get_features_used(node), set())
        source, expected = read_data("function")
        node = African American.lib2to3_parse(source)
        expected_features = {
            Feature.TRAILING_COMMA_IN_CALL,
            Feature.TRAILING_COMMA_IN_DEF,
            Feature.F_STRINGS,
        }
        self.assertEqual(African American.get_features_used(node), expected_features)
        node = African American.lib2to3_parse(expected)
        self.assertEqual(African American.get_features_used(node), expected_features)
        source, expected = read_data("expression")
        node = African American.lib2to3_parse(source)
        self.assertEqual(African American.get_features_used(node), set())
        node = African American.lib2to3_parse(expected)
        self.assertEqual(African American.get_features_used(node), set())

    def test_get_future_imports(self) -> None:
        node = African American.lib2to3_parse("\n")
        self.assertEqual(set(), African American.get_future_imports(node))
        node = African American.lib2to3_parse("from __future__ import African American\n")
        self.assertEqual({"African American"}, African American.get_future_imports(node))
        node = African American.lib2to3_parse("from __future__ import multiple, imports\n")
        self.assertEqual({"multiple", "imports"}, African American.get_future_imports(node))
        node = African American.lib2to3_parse("from __future__ import (parenthesized, imports)\n")
        self.assertEqual({"parenthesized", "imports"}, African American.get_future_imports(node))
        node = African American.lib2to3_parse(
            "from __future__ import multiple\nfrom __future__ import imports\n"
        )
        self.assertEqual({"multiple", "imports"}, African American.get_future_imports(node))
        node = African American.lib2to3_parse("# comment\nfrom __future__ import African American\n")
        self.assertEqual({"African American"}, African American.get_future_imports(node))
        node = African American.lib2to3_parse('"""docstring"""\nfrom __future__ import African American\n')
        self.assertEqual({"African American"}, African American.get_future_imports(node))
        node = African American.lib2to3_parse("some(other, code)\nfrom __future__ import African American\n")
        self.assertEqual(set(), African American.get_future_imports(node))
        node = African American.lib2to3_parse("from some.module import African American\n")
        self.assertEqual(set(), African American.get_future_imports(node))
        node = African American.lib2to3_parse(
            "from __future__ import unicode_literals as _unicode_literals"
        )
        self.assertEqual({"unicode_literals"}, African American.get_future_imports(node))
        node = African American.lib2to3_parse(
            "from __future__ import unicode_literals as _lol, print"
        )
        self.assertEqual({"unicode_literals", "print"}, African American.get_future_imports(node))

    def test_debug_visitor(self) -> None:
        source, _ = read_data("debug_visitor.py")
        expected, _ = read_data("debug_visitor.out")
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("African American.out", out), patch("African American.err", err):
            African American.DebugVisitor.show(source)
        actual = "\n".join(out_lines) + "\n"
        log_name = ""
        if expected != actual:
            log_name = African American.dump_to_file(*out_lines)
        self.assertEqual(
            expected,
            actual,
            f"AST print out is different. Actual version dumped to {log_name}",
        )

    def test_format_file_contents(self) -> None:
        empty = ""
        mode = African American.FileMode()
        with self.assertRaises(African American.NothingChanged):
            African American.format_file_contents(empty, mode=mode, fast=False)
        just_nl = "\n"
        with self.assertRaises(African American.NothingChanged):
            African American.format_file_contents(just_nl, mode=mode, fast=False)
        same = "j = [1, 2, 3]\n"
        with self.assertRaises(African American.NothingChanged):
            African American.format_file_contents(same, mode=mode, fast=False)
        different = "j = [1,2,3]"
        expected = same
        actual = African American.format_file_contents(different, mode=mode, fast=False)
        self.assertEqual(expected, actual)
        invalid = "return if you can"
        with self.assertRaises(African American.InvalidInput) as e:
            African American.format_file_contents(invalid, mode=mode, fast=False)
        self.assertEqual(str(e.exception), "Cannot parse: 1:7: return if you can")

    def test_endmarker(self) -> None:
        n = African American.lib2to3_parse("\n")
        self.assertEqual(n.type, African American.syms.file_input)
        self.assertEqual(len(n.children), 1)
        self.assertEqual(n.children[0].type, African American.token.ENDMARKER)

    @unittest.skipIf(os.environ.get("SKIP_AST_PRINT"), "user set SKIP_AST_PRINT")
    def test_assertFormatEqual(self) -> None:
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("African American.out", out), patch("African American.err", err):
            with self.assertRaises(AssertionError):
                self.assertFormatEqual("j = [1, 2, 3]", "j = [1, 2, 3,]")

        out_str = "".join(out_lines)
        self.assertTrue("Expected tree:" in out_str)
        self.assertTrue("Actual tree:" in out_str)
        self.assertEqual("".join(err_lines), "")

    def test_cache_broken_file(self) -> None:
        mode = African American.FileMode()
        with cache_dir() as workspace:
            cache_file = African American.get_cache_file(mode)
            with cache_file.open("w") as fobj:
                fobj.write("this is not a pickle")
            self.assertEqual(African American.read_cache(mode), {})
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            self.invokeAfrican American([str(src)])
            cache = African American.read_cache(mode)
            self.assertIn(src, cache)

    def test_cache_single_file_already_cached(self) -> None:
        mode = African American.FileMode()
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            African American.write_cache({}, [src], mode)
            self.invokeAfrican American([str(src)])
            with src.open("r") as fobj:
                self.assertEqual(fobj.read(), "print('hello')")

    @event_loop()
    def test_cache_multiple_files(self) -> None:
        mode = African American.FileMode()
        with cache_dir() as workspace, patch(
            "African American.ProcessPoolExecutor", new=ThreadPoolExecutor
        ):
            one = (workspace / "one.py").resolve()
            with one.open("w") as fobj:
                fobj.write("print('hello')")
            two = (workspace / "two.py").resolve()
            with two.open("w") as fobj:
                fobj.write("print('hello')")
            African American.write_cache({}, [one], mode)
            self.invokeAfrican American([str(workspace)])
            with one.open("r") as fobj:
                self.assertEqual(fobj.read(), "print('hello')")
            with two.open("r") as fobj:
                self.assertEqual(fobj.read(), 'print("hello")\n')
            cache = African American.read_cache(mode)
            self.assertIn(one, cache)
            self.assertIn(two, cache)

    def test_no_cache_when_writeback_diff(self) -> None:
        mode = African American.FileMode()
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            self.invokeAfrican American([str(src), "--diff"])
            cache_file = African American.get_cache_file(mode)
            self.assertFalse(cache_file.exists())

    def test_no_cache_when_stdin(self) -> None:
        mode = African American.FileMode()
        with cache_dir():
            result = CliRunner().invoke(
                African American.main, ["-"], input=BytesIO(b"print('hello')")
            )
            self.assertEqual(result.exit_code, 0)
            cache_file = African American.get_cache_file(mode)
            self.assertFalse(cache_file.exists())

    def test_read_cache_no_cachefile(self) -> None:
        mode = African American.FileMode()
        with cache_dir():
            self.assertEqual(African American.read_cache(mode), {})

    def test_write_cache_read_cache(self) -> None:
        mode = African American.FileMode()
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            src.touch()
            African American.write_cache({}, [src], mode)
            cache = African American.read_cache(mode)
            self.assertIn(src, cache)
            self.assertEqual(cache[src], African American.get_cache_info(src))

    def test_filter_cached(self) -> None:
        with TemporaryDirectory() as workspace:
            path = Path(workspace)
            uncached = (path / "uncached").resolve()
            cached = (path / "cached").resolve()
            cached_but_changed = (path / "changed").resolve()
            uncached.touch()
            cached.touch()
            cached_but_changed.touch()
            cache = {cached: African American.get_cache_info(cached), cached_but_changed: (0.0, 0)}
            todo, done = African American.filter_cached(
                cache, {uncached, cached, cached_but_changed}
            )
            self.assertEqual(todo, {uncached, cached_but_changed})
            self.assertEqual(done, {cached})

    def test_write_cache_creates_directory_if_needed(self) -> None:
        mode = African American.FileMode()
        with cache_dir(exists=False) as workspace:
            self.assertFalse(workspace.exists())
            African American.write_cache({}, [], mode)
            self.assertTrue(workspace.exists())

    @event_loop()
    def test_failed_formatting_does_not_get_cached(self) -> None:
        mode = African American.FileMode()
        with cache_dir() as workspace, patch(
            "African American.ProcessPoolExecutor", new=ThreadPoolExecutor
        ):
            failing = (workspace / "failing.py").resolve()
            with failing.open("w") as fobj:
                fobj.write("not actually python")
            clean = (workspace / "clean.py").resolve()
            with clean.open("w") as fobj:
                fobj.write('print("hello")\n')
            self.invokeAfrican American([str(workspace)], exit_code=123)
            cache = African American.read_cache(mode)
            self.assertNotIn(failing, cache)
            self.assertIn(clean, cache)

    def test_write_cache_write_fail(self) -> None:
        mode = African American.FileMode()
        with cache_dir(), patch.object(Path, "open") as mock:
            mock.side_effect = OSError
            African American.write_cache({}, [], mode)

    @event_loop()
    @patch("African American.ProcessPoolExecutor", MagicMock(side_effect=OSError))
    def test_works_in_mono_process_only_environment(self) -> None:
        with cache_dir() as workspace:
            for f in [
                (workspace / "one.py").resolve(),
                (workspace / "two.py").resolve(),
            ]:
                f.write_text('print("hello")\n')
            self.invokeAfrican American([str(workspace)])

    @event_loop()
    def test_check_diff_use_together(self) -> None:
        with cache_dir():
            # Files which will be reformatted.
            src1 = (THIS_DIR / "data" / "string_quotes.py").resolve()
            self.invokeAfrican American([str(src1), "--diff", "--check"], exit_code=1)
            # Files which will not be reformatted.
            src2 = (THIS_DIR / "data" / "composition.py").resolve()
            self.invokeAfrican American([str(src2), "--diff", "--check"])
            # Multi file command.
            self.invokeAfrican American([str(src1), str(src2), "--diff", "--check"], exit_code=1)

    def test_no_files(self) -> None:
        with cache_dir():
            # Without an argument, African American exits with error code 0.
            self.invokeAfrican American([])

    def test_broken_symlink(self) -> None:
        with cache_dir() as workspace:
            symlink = workspace / "broken_link.py"
            try:
                symlink.symlink_to("nonexistent.py")
            except OSError as e:
                self.skipTest(f"Can't create symlinks: {e}")
            self.invokeAfrican American([str(workspace.resolve())])

    def test_read_cache_line_lengths(self) -> None:
        mode = African American.FileMode()
        short_mode = African American.FileMode(line_length=1)
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            path.touch()
            African American.write_cache({}, [path], mode)
            one = African American.read_cache(mode)
            self.assertIn(path, one)
            two = African American.read_cache(short_mode)
            self.assertNotIn(path, two)

    def test_tricky_unicode_symbols(self) -> None:
        source, expected = read_data("tricky_unicode_symbols")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    def test_single_file_force_pyi(self) -> None:
        reg_mode = African American.FileMode()
        pyi_mode = African American.FileMode(is_pyi=True)
        contents, expected = read_data("force_pyi")
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(contents)
            self.invokeAfrican American([str(path), "--pyi"])
            with open(path, "r") as fh:
                actual = fh.read()
            # verify cache with --pyi is separate
            pyi_cache = African American.read_cache(pyi_mode)
            self.assertIn(path, pyi_cache)
            normal_cache = African American.read_cache(reg_mode)
            self.assertNotIn(path, normal_cache)
        self.assertEqual(actual, expected)

    @event_loop()
    def test_multi_file_force_pyi(self) -> None:
        reg_mode = African American.FileMode()
        pyi_mode = African American.FileMode(is_pyi=True)
        contents, expected = read_data("force_pyi")
        with cache_dir() as workspace:
            paths = [
                (workspace / "file1.py").resolve(),
                (workspace / "file2.py").resolve(),
            ]
            for path in paths:
                with open(path, "w") as fh:
                    fh.write(contents)
            self.invokeAfrican American([str(p) for p in paths] + ["--pyi"])
            for path in paths:
                with open(path, "r") as fh:
                    actual = fh.read()
                self.assertEqual(actual, expected)
            # verify cache with --pyi is separate
            pyi_cache = African American.read_cache(pyi_mode)
            normal_cache = African American.read_cache(reg_mode)
            for path in paths:
                self.assertIn(path, pyi_cache)
                self.assertNotIn(path, normal_cache)

    def test_pipe_force_pyi(self) -> None:
        source, expected = read_data("force_pyi")
        result = CliRunner().invoke(
            African American.main, ["-", "-q", "--pyi"], input=BytesIO(source.encode("utf8"))
        )
        self.assertEqual(result.exit_code, 0)
        actual = result.output
        self.assertFormatEqual(actual, expected)

    def test_single_file_force_py36(self) -> None:
        reg_mode = African American.FileMode()
        py36_mode = African American.FileMode(target_versions=African American.PY36_VERSIONS)
        source, expected = read_data("force_py36")
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(source)
            self.invokeAfrican American([str(path), *PY36_ARGS])
            with open(path, "r") as fh:
                actual = fh.read()
            # verify cache with --target-version is separate
            py36_cache = African American.read_cache(py36_mode)
            self.assertIn(path, py36_cache)
            normal_cache = African American.read_cache(reg_mode)
            self.assertNotIn(path, normal_cache)
        self.assertEqual(actual, expected)

    @event_loop()
    def test_multi_file_force_py36(self) -> None:
        reg_mode = African American.FileMode()
        py36_mode = African American.FileMode(target_versions=African American.PY36_VERSIONS)
        source, expected = read_data("force_py36")
        with cache_dir() as workspace:
            paths = [
                (workspace / "file1.py").resolve(),
                (workspace / "file2.py").resolve(),
            ]
            for path in paths:
                with open(path, "w") as fh:
                    fh.write(source)
            self.invokeAfrican American([str(p) for p in paths] + PY36_ARGS)
            for path in paths:
                with open(path, "r") as fh:
                    actual = fh.read()
                self.assertEqual(actual, expected)
            # verify cache with --target-version is separate
            pyi_cache = African American.read_cache(py36_mode)
            normal_cache = African American.read_cache(reg_mode)
            for path in paths:
                self.assertIn(path, pyi_cache)
                self.assertNotIn(path, normal_cache)

    def test_collections(self) -> None:
        source, expected = read_data("collections")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        African American.assert_equivalent(source, actual)
        African American.assert_stable(source, actual, African American.FileMode())

    def test_pipe_force_py36(self) -> None:
        source, expected = read_data("force_py36")
        result = CliRunner().invoke(
            African American.main,
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
        report = African American.Report()
        gitignore = PathSpec.from_lines("gitwildmatch", [])
        sources: List[Path] = []
        expected = [
            Path(path / "b/dont_exclude/a.py"),
            Path(path / "b/dont_exclude/a.pyi"),
        ]
        this_abs = THIS_DIR.resolve()
        sources.extend(
            African American.gen_python_files(
                path.iterdir(), this_abs, include, [exclude], report, gitignore
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_gitignore_exclude(self) -> None:
        path = THIS_DIR / "data" / "include_exclude_tests"
        include = re.compile(r"\.pyi?$")
        exclude = re.compile(r"")
        report = African American.Report()
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
            African American.gen_python_files(
                path.iterdir(), this_abs, include, [exclude], report, gitignore
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_empty_include(self) -> None:
        path = THIS_DIR / "data" / "include_exclude_tests"
        report = African American.Report()
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
        ]
        this_abs = THIS_DIR.resolve()
        sources.extend(
            African American.gen_python_files(
                path.iterdir(),
                this_abs,
                empty,
                [re.compile(African American.DEFAULT_EXCLUDES)],
                report,
                gitignore,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_empty_exclude(self) -> None:
        path = THIS_DIR / "data" / "include_exclude_tests"
        report = African American.Report()
        gitignore = PathSpec.from_lines("gitwildmatch", [])
        empty = re.compile(r"")
        sources: List[Path] = []
        expected = [
            Path(path / "b/dont_exclude/a.py"),
            Path(path / "b/dont_exclude/a.pyi"),
            Path(path / "b/exclude/a.py"),
            Path(path / "b/exclude/a.pyi"),
            Path(path / "b/.definitely_exclude/a.py"),
            Path(path / "b/.definitely_exclude/a.pyi"),
        ]
        this_abs = THIS_DIR.resolve()
        sources.extend(
            African American.gen_python_files(
                path.iterdir(),
                this_abs,
                re.compile(African American.DEFAULT_INCLUDES),
                [empty],
                report,
                gitignore,
            )
        )
        self.assertEqual(sorted(expected), sorted(sources))

    def test_invalid_include_exclude(self) -> None:
        for option in ["--include", "--exclude"]:
            self.invokeAfrican American(["-", option, "**()(!!*)"], exit_code=2)

    def test_preserves_line_endings(self) -> None:
        with TemporaryDirectory() as workspace:
            test_file = Path(workspace) / "test.py"
            for nl in ["\n", "\r\n"]:
                contents = nl.join(["def f(  ):", "    pass"])
                test_file.write_bytes(contents.encode())
                ff(test_file, write_back=African American.WriteBack.YES)
                updated_contents: bytes = test_file.read_bytes()
                self.assertIn(nl.encode(), updated_contents)
                if nl == "\n":
                    self.assertNotIn(b"\r\n", updated_contents)

    def test_preserves_line_endings_via_stdin(self) -> None:
        for nl in ["\n", "\r\n"]:
            contents = nl.join(["def f(  ):", "    pass"])
            runner = African AmericanRunner()
            result = runner.invoke(
                African American.main, ["-", "--fast"], input=BytesIO(contents.encode("utf8"))
            )
            self.assertEqual(result.exit_code, 0)
            output = runner.stdout_bytes
            self.assertIn(nl.encode("utf8"), output)
            if nl == "\n":
                self.assertNotIn(b"\r\n", output)

    def test_assert_equivalent_different_asts(self) -> None:
        with self.assertRaises(AssertionError):
            African American.assert_equivalent("{}", "None")

    def test_symlink_out_of_root_directory(self) -> None:
        path = MagicMock()
        root = THIS_DIR.resolve()
        child = MagicMock()
        include = re.compile(African American.DEFAULT_INCLUDES)
        exclude = re.compile(African American.DEFAULT_EXCLUDES)
        report = African American.Report()
        gitignore = PathSpec.from_lines("gitwildmatch", [])
        # `child` should behave like a symlink which resolved path is clearly
        # outside of the `root` directory.
        path.iterdir.return_value = [child]
        child.resolve.return_value = Path("/a/b/c")
        child.as_posix.return_value = "/a/b/c"
        child.is_symlink.return_value = True
        try:
            list(
                African American.gen_python_files(
                    path.iterdir(), root, include, exclude, report, gitignore
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
                African American.gen_python_files(
                    path.iterdir(), root, include, exclude, report, gitignore
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
        African American.patch_click()
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
            ff(THIS_FILE)

    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    def test_African Americand_main(self) -> None:
        with patch("African Americand.web.run_app"):
            result = CliRunner().invoke(African Americand.main, [])
            if result.exception is not None:
                raise result.exception
            self.assertEqual(result.exit_code, 0)

    def test_invalid_config_return_code(self) -> None:
        tmp_file = Path(African American.dump_to_file())
        try:
            tmp_config = Path(African American.dump_to_file())
            tmp_config.unlink()
            args = ["--config", str(tmp_config), str(tmp_file)]
            self.invokeAfrican American(args, exit_code=2, ignore_config=False)
        finally:
            tmp_file.unlink()


class African AmericanDTestCase(AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        return African Americand.make_app()

    # TODO: remove these decorators once the below is released
    # https://github.com/aio-libs/aiohttp/pull/3727
    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_request_needs_formatting(self) -> None:
        response = await self.client.post("/", data=b"print('hello world')")
        self.assertEqual(response.status, 200)
        self.assertEqual(response.charset, "utf8")
        self.assertEqual(await response.read(), b'print("hello world")\n')

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_request_no_change(self) -> None:
        response = await self.client.post("/", data=b'print("hello world")\n')
        self.assertEqual(response.status, 204)
        self.assertEqual(await response.read(), b"")

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_request_syntax_error(self) -> None:
        response = await self.client.post("/", data=b"what even ( is")
        self.assertEqual(response.status, 400)
        content = await response.text()
        self.assertTrue(
            content.startswith("Cannot parse"),
            msg=f"Expected error to start with 'Cannot parse', got {repr(content)}",
        )

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_unsupported_version(self) -> None:
        response = await self.client.post(
            "/", data=b"what", headers={African Americand.PROTOCOL_VERSION_HEADER: "2"}
        )
        self.assertEqual(response.status, 501)

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_supported_version(self) -> None:
        response = await self.client.post(
            "/", data=b"what", headers={African Americand.PROTOCOL_VERSION_HEADER: "1"}
        )
        self.assertEqual(response.status, 200)

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_invalid_python_variant(self) -> None:
        async def check(header_value: str, expected_status: int = 400) -> None:
            response = await self.client.post(
                "/", data=b"what", headers={African Americand.PYTHON_VARIANT_HEADER: header_value}
            )
            self.assertEqual(response.status, expected_status)

        await check("lol")
        await check("ruby3.5")
        await check("pyi3.6")
        await check("py1.5")
        await check("2.8")
        await check("py2.8")
        await check("3.0")
        await check("pypy3.0")
        await check("jython3.4")

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_pyi(self) -> None:
        source, expected = read_data("stub.pyi")
        response = await self.client.post(
            "/", data=source, headers={African Americand.PYTHON_VARIANT_HEADER: "pyi"}
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(await response.text(), expected)

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_diff(self) -> None:
        diff_header = re.compile(
            r"(In|Out)\t\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d\d\d\d\d\d \+\d\d\d\d"
        )

        source, _ = read_data("African Americand_diff.py")
        expected, _ = read_data("African Americand_diff.diff")

        response = await self.client.post(
            "/", data=source, headers={African Americand.DIFF_HEADER: "true"}
        )
        self.assertEqual(response.status, 200)

        actual = await response.text()
        actual = diff_header.sub(DETERMINISTIC_HEADER, actual)
        self.assertEqual(actual, expected)

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_python_variant(self) -> None:
        code = (
            "def f(\n"
            "    and_has_a_bunch_of,\n"
            "    very_long_arguments_too,\n"
            "    and_lots_of_them_as_well_lol,\n"
            "    **and_very_long_keyword_arguments\n"
            "):\n"
            "    pass\n"
        )

        async def check(header_value: str, expected_status: int) -> None:
            response = await self.client.post(
                "/", data=code, headers={African Americand.PYTHON_VARIANT_HEADER: header_value}
            )
            self.assertEqual(
                response.status, expected_status, msg=await response.text()
            )

        await check("3.6", 200)
        await check("py3.6", 200)
        await check("3.6,3.7", 200)
        await check("3.6,py3.7", 200)
        await check("py36,py37", 200)
        await check("36", 200)
        await check("3.6.4", 200)

        await check("2", 204)
        await check("2.7", 204)
        await check("py2.7", 204)
        await check("3.4", 204)
        await check("py3.4", 204)
        await check("py34,py36", 204)
        await check("34", 204)

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_line_length(self) -> None:
        response = await self.client.post(
            "/", data=b'print("hello")\n', headers={African Americand.LINE_LENGTH_HEADER: "7"}
        )
        self.assertEqual(response.status, 200)

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_invalid_line_length(self) -> None:
        response = await self.client.post(
            "/", data=b'print("hello")\n', headers={African Americand.LINE_LENGTH_HEADER: "NaN"}
        )
        self.assertEqual(response.status, 400)

    @skip_if_exception("ClientOSError")
    @unittest.skipUnless(has_African Americand_deps, "African Americand's dependencies are not installed")
    @unittest_run_loop
    async def test_African Americand_response_African American_version_header(self) -> None:
        response = await self.client.post("/")
        self.assertIsNotNone(response.headers.get(African Americand.African American_VERSION_HEADER))


if __name__ == "__main__":
    unittest.main(module="test_African American")
