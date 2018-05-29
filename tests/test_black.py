#!/usr/bin/env python3
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial
from io import StringIO
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Any, List, Tuple, Iterator
import unittest
from unittest.mock import patch

from click import unstyle
from click.testing import CliRunner

import black

ll = 88
ff = partial(black.format_file_in_place, line_length=ll, fast=True)
fs = partial(black.format_str, line_length=ll)
THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent
EMPTY_LINE = "# EMPTY LINE WITH WHITESPACE" + " (this comment will be removed)"


def dump_to_stderr(*output: str) -> str:
    return "\n" + "\n".join(output) + "\n"


def read_data(name: str) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    if not name.endswith((".py", ".pyi", ".out", ".diff")):
        name += ".py"
    _input: List[str] = []
    _output: List[str] = []
    with open(THIS_DIR / name, "r", encoding="utf8") as test:
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
        with patch("black.CACHE_DIR", cache_dir):
            yield cache_dir


@contextmanager
def event_loop(close: bool) -> Iterator[None]:
    policy = asyncio.get_event_loop_policy()
    old_loop = policy.get_event_loop()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield

    finally:
        policy.set_event_loop(old_loop)
        if close:
            loop.close()


class BlackTestCase(unittest.TestCase):
    maxDiff = None

    def assertFormatEqual(self, expected: str, actual: str) -> None:
        if actual != expected and not os.environ.get("SKIP_AST_PRINT"):
            bdv: black.DebugVisitor[Any]
            black.out("Expected tree:", fg="green")
            try:
                exp_node = black.lib2to3_parse(expected)
                bdv = black.DebugVisitor()
                list(bdv.visit(exp_node))
            except Exception as ve:
                black.err(str(ve))
            black.out("Actual tree:", fg="red")
            try:
                exp_node = black.lib2to3_parse(actual)
                bdv = black.DebugVisitor()
                list(bdv.visit(exp_node))
            except Exception as ve:
                black.err(str(ve))
        self.assertEqual(expected, actual)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_self(self) -> None:
        source, expected = read_data("test_black")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)
        self.assertFalse(ff(THIS_FILE))

    @patch("black.dump_to_file", dump_to_stderr)
    def test_black(self) -> None:
        source, expected = read_data("../black")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)
        self.assertFalse(ff(THIS_DIR / ".." / "black.py"))

    def test_piping(self) -> None:
        source, expected = read_data("../black")
        hold_stdin, hold_stdout = sys.stdin, sys.stdout
        try:
            sys.stdin, sys.stdout = StringIO(source), StringIO()
            sys.stdin.name = "<stdin>"
            black.format_stdin_to_stdout(
                line_length=ll, fast=True, write_back=black.WriteBack.YES
            )
            sys.stdout.seek(0)
            actual = sys.stdout.read()
        finally:
            sys.stdin, sys.stdout = hold_stdin, hold_stdout
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    def test_piping_diff(self) -> None:
        source, _ = read_data("expression.py")
        expected, _ = read_data("expression.diff")
        hold_stdin, hold_stdout = sys.stdin, sys.stdout
        try:
            sys.stdin, sys.stdout = StringIO(source), StringIO()
            sys.stdin.name = "<stdin>"
            black.format_stdin_to_stdout(
                line_length=ll, fast=True, write_back=black.WriteBack.DIFF
            )
            sys.stdout.seek(0)
            actual = sys.stdout.read()
        finally:
            sys.stdin, sys.stdout = hold_stdin, hold_stdout
        actual = actual.rstrip() + "\n"  # the diff output has a trailing space
        self.assertEqual(expected, actual)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_setup(self) -> None:
        source, expected = read_data("../setup")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)
        self.assertFalse(ff(THIS_DIR / ".." / "setup.py"))

    @patch("black.dump_to_file", dump_to_stderr)
    def test_function(self) -> None:
        source, expected = read_data("function")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_function2(self) -> None:
        source, expected = read_data("function2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_expression(self) -> None:
        source, expected = read_data("expression")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

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
            black.assert_stable(source, actual, line_length=ll)

    def test_expression_diff(self) -> None:
        source, _ = read_data("expression.py")
        expected, _ = read_data("expression.diff")
        tmp_file = Path(black.dump_to_file(source))
        hold_stdout = sys.stdout
        try:
            sys.stdout = StringIO()
            self.assertTrue(ff(tmp_file, write_back=black.WriteBack.DIFF))
            sys.stdout.seek(0)
            actual = sys.stdout.read()
            actual = actual.replace(str(tmp_file), "<stdin>")
        finally:
            sys.stdout = hold_stdout
            os.unlink(tmp_file)
        actual = actual.rstrip() + "\n"  # the diff output has a trailing space
        if expected != actual:
            dump = black.dump_to_file(actual)
            msg = (
                f"Expected diff isn't equal to the actual. If you made changes "
                f"to expression.py and this is an anticipated difference, "
                f"overwrite tests/expression.diff with {dump}"
            )
            self.assertEqual(expected, actual, msg)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_fstring(self) -> None:
        source, expected = read_data("fstring")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_string_quotes(self) -> None:
        source, expected = read_data("string_quotes")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_slices(self) -> None:
        source, expected = read_data("slices")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_comments(self) -> None:
        source, expected = read_data("comments")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_comments2(self) -> None:
        source, expected = read_data("comments2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_comments3(self) -> None:
        source, expected = read_data("comments3")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_comments4(self) -> None:
        source, expected = read_data("comments4")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_comments5(self) -> None:
        source, expected = read_data("comments5")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_cantfit(self) -> None:
        source, expected = read_data("cantfit")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_import_spacing(self) -> None:
        source, expected = read_data("import_spacing")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_composition(self) -> None:
        source, expected = read_data("composition")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_empty_lines(self) -> None:
        source, expected = read_data("empty_lines")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_string_prefixes(self) -> None:
        source, expected = read_data("string_prefixes")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_python2(self) -> None:
        source, expected = read_data("python2")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        # black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_python2_unicode_literals(self) -> None:
        source, expected = read_data("python2_unicode_literals")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_stub(self) -> None:
        mode = black.FileMode.PYI
        source, expected = read_data("stub.pyi")
        actual = fs(source, mode=mode)
        self.assertFormatEqual(expected, actual)
        black.assert_stable(source, actual, line_length=ll, mode=mode)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_fmtonoff(self) -> None:
        source, expected = read_data("fmtonoff")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_remove_empty_parentheses_after_class(self) -> None:
        source, expected = read_data("class_blank_parentheses")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_new_line_between_class_and_code(self) -> None:
        source, expected = read_data("class_methods_new_line")
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    def test_report(self) -> None:
        report = black.Report()
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("black.out", out), patch("black.err", err):
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
                "1 file reformatted, 2 files left unchanged, "
                "1 file failed to reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f3"), black.Changed.YES)
            self.assertEqual(len(out_lines), 4)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(out_lines[-1], "reformatted f3")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, "
                "1 file failed to reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.failed(Path("e2"), "boom")
            self.assertEqual(len(out_lines), 4)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(err_lines[-1], "error: cannot format e2: boom")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, "
                "2 files failed to reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path("f4"), black.Changed.NO)
            self.assertEqual(len(out_lines), 5)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(out_lines[-1], "f4 already well formatted, good job.")
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 3 files left unchanged, "
                "2 files failed to reformat.",
            )
            self.assertEqual(report.return_code, 123)
            report.check = True
            self.assertEqual(
                unstyle(str(report)),
                "2 files would be reformatted, 3 files would be left unchanged, "
                "2 files would fail to reformat.",
            )

    def test_is_python36(self) -> None:
        node = black.lib2to3_parse("def f(*, arg): ...\n")
        self.assertFalse(black.is_python36(node))
        node = black.lib2to3_parse("def f(*, arg,): ...\n")
        self.assertTrue(black.is_python36(node))
        node = black.lib2to3_parse("def f(*, arg): f'string'\n")
        self.assertTrue(black.is_python36(node))
        source, expected = read_data("function")
        node = black.lib2to3_parse(source)
        self.assertTrue(black.is_python36(node))
        node = black.lib2to3_parse(expected)
        self.assertTrue(black.is_python36(node))
        source, expected = read_data("expression")
        node = black.lib2to3_parse(source)
        self.assertFalse(black.is_python36(node))
        node = black.lib2to3_parse(expected)
        self.assertFalse(black.is_python36(node))

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

    def test_debug_visitor(self) -> None:
        source, _ = read_data("debug_visitor.py")
        expected, _ = read_data("debug_visitor.out")
        out_lines = []
        err_lines = []

        def out(msg: str, **kwargs: Any) -> None:
            out_lines.append(msg)

        def err(msg: str, **kwargs: Any) -> None:
            err_lines.append(msg)

        with patch("black.out", out), patch("black.err", err):
            black.DebugVisitor.show(source)
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
        with self.assertRaises(black.NothingChanged):
            black.format_file_contents(empty, line_length=ll, fast=False)
        just_nl = "\n"
        with self.assertRaises(black.NothingChanged):
            black.format_file_contents(just_nl, line_length=ll, fast=False)
        same = "l = [1, 2, 3]\n"
        with self.assertRaises(black.NothingChanged):
            black.format_file_contents(same, line_length=ll, fast=False)
        different = "l = [1,2,3]"
        expected = same
        actual = black.format_file_contents(different, line_length=ll, fast=False)
        self.assertEqual(expected, actual)
        invalid = "return if you can"
        with self.assertRaises(ValueError) as e:
            black.format_file_contents(invalid, line_length=ll, fast=False)
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

        with patch("black.out", out), patch("black.err", err):
            with self.assertRaises(AssertionError):
                self.assertFormatEqual("l = [1, 2, 3]", "l = [1, 2, 3,]")

        out_str = "".join(out_lines)
        self.assertTrue("Expected tree:" in out_str)
        self.assertTrue("Actual tree:" in out_str)
        self.assertEqual("".join(err_lines), "")

    def test_cache_broken_file(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir() as workspace:
            cache_file = black.get_cache_file(black.DEFAULT_LINE_LENGTH, mode)
            with cache_file.open("w") as fobj:
                fobj.write("this is not a pickle")
            self.assertEqual(black.read_cache(black.DEFAULT_LINE_LENGTH, mode), {})
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            result = CliRunner().invoke(black.main, [str(src)])
            self.assertEqual(result.exit_code, 0)
            cache = black.read_cache(black.DEFAULT_LINE_LENGTH, mode)
            self.assertIn(src, cache)

    def test_cache_single_file_already_cached(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            black.write_cache({}, [src], black.DEFAULT_LINE_LENGTH, mode)
            result = CliRunner().invoke(black.main, [str(src)])
            self.assertEqual(result.exit_code, 0)
            with src.open("r") as fobj:
                self.assertEqual(fobj.read(), "print('hello')")

    @event_loop(close=False)
    def test_cache_multiple_files(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir() as workspace, patch(
            "black.ProcessPoolExecutor", new=ThreadPoolExecutor
        ):
            one = (workspace / "one.py").resolve()
            with one.open("w") as fobj:
                fobj.write("print('hello')")
            two = (workspace / "two.py").resolve()
            with two.open("w") as fobj:
                fobj.write("print('hello')")
            black.write_cache({}, [one], black.DEFAULT_LINE_LENGTH, mode)
            result = CliRunner().invoke(black.main, [str(workspace)])
            self.assertEqual(result.exit_code, 0)
            with one.open("r") as fobj:
                self.assertEqual(fobj.read(), "print('hello')")
            with two.open("r") as fobj:
                self.assertEqual(fobj.read(), 'print("hello")\n')
            cache = black.read_cache(black.DEFAULT_LINE_LENGTH, mode)
            self.assertIn(one, cache)
            self.assertIn(two, cache)

    def test_no_cache_when_writeback_diff(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            with src.open("w") as fobj:
                fobj.write("print('hello')")
            result = CliRunner().invoke(black.main, [str(src), "--diff"])
            self.assertEqual(result.exit_code, 0)
            cache_file = black.get_cache_file(black.DEFAULT_LINE_LENGTH, mode)
            self.assertFalse(cache_file.exists())

    def test_no_cache_when_stdin(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir():
            result = CliRunner().invoke(black.main, ["-"], input="print('hello')")
            self.assertEqual(result.exit_code, 0)
            cache_file = black.get_cache_file(black.DEFAULT_LINE_LENGTH, mode)
            self.assertFalse(cache_file.exists())

    def test_read_cache_no_cachefile(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir():
            self.assertEqual(black.read_cache(black.DEFAULT_LINE_LENGTH, mode), {})

    def test_write_cache_read_cache(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir() as workspace:
            src = (workspace / "test.py").resolve()
            src.touch()
            black.write_cache({}, [src], black.DEFAULT_LINE_LENGTH, mode)
            cache = black.read_cache(black.DEFAULT_LINE_LENGTH, mode)
            self.assertIn(src, cache)
            self.assertEqual(cache[src], black.get_cache_info(src))

    def test_filter_cached(self) -> None:
        with TemporaryDirectory() as workspace:
            path = Path(workspace)
            uncached = (path / "uncached").resolve()
            cached = (path / "cached").resolve()
            cached_but_changed = (path / "changed").resolve()
            uncached.touch()
            cached.touch()
            cached_but_changed.touch()
            cache = {cached: black.get_cache_info(cached), cached_but_changed: (0.0, 0)}
            todo, done = black.filter_cached(
                cache, [uncached, cached, cached_but_changed]
            )
            self.assertEqual(todo, [uncached, cached_but_changed])
            self.assertEqual(done, [cached])

    def test_write_cache_creates_directory_if_needed(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir(exists=False) as workspace:
            self.assertFalse(workspace.exists())
            black.write_cache({}, [], black.DEFAULT_LINE_LENGTH, mode)
            self.assertTrue(workspace.exists())

    @event_loop(close=False)
    def test_failed_formatting_does_not_get_cached(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir() as workspace, patch(
            "black.ProcessPoolExecutor", new=ThreadPoolExecutor
        ):
            failing = (workspace / "failing.py").resolve()
            with failing.open("w") as fobj:
                fobj.write("not actually python")
            clean = (workspace / "clean.py").resolve()
            with clean.open("w") as fobj:
                fobj.write('print("hello")\n')
            result = CliRunner().invoke(black.main, [str(workspace)])
            self.assertEqual(result.exit_code, 123)
            cache = black.read_cache(black.DEFAULT_LINE_LENGTH, mode)
            self.assertNotIn(failing, cache)
            self.assertIn(clean, cache)

    def test_write_cache_write_fail(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir(), patch.object(Path, "open") as mock:
            mock.side_effect = OSError
            black.write_cache({}, [], black.DEFAULT_LINE_LENGTH, mode)

    @event_loop(close=False)
    def test_check_diff_use_together(self) -> None:
        with cache_dir():
            # Files which will be reformatted.
            src1 = (THIS_DIR / "string_quotes.py").resolve()
            result = CliRunner().invoke(black.main, [str(src1), "--diff", "--check"])
            self.assertEqual(result.exit_code, 1)

            # Files which will not be reformatted.
            src2 = (THIS_DIR / "composition.py").resolve()
            result = CliRunner().invoke(black.main, [str(src2), "--diff", "--check"])
            self.assertEqual(result.exit_code, 0)

            # Multi file command.
            result = CliRunner().invoke(
                black.main, [str(src1), str(src2), "--diff", "--check"]
            )
            self.assertEqual(result.exit_code, 1, result.output)

    def test_no_files(self) -> None:
        with cache_dir():
            # Without an argument, black exits with error code 0.
            result = CliRunner().invoke(black.main, [])
            self.assertEqual(result.exit_code, 0)

    def test_broken_symlink(self) -> None:
        with cache_dir() as workspace:
            symlink = workspace / "broken_link.py"
            symlink.symlink_to("nonexistent.py")
            result = CliRunner().invoke(black.main, [str(workspace.resolve())])
            self.assertEqual(result.exit_code, 0)

    def test_read_cache_line_lengths(self) -> None:
        mode = black.FileMode.AUTO_DETECT
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            path.touch()
            black.write_cache({}, [path], 1, mode)
            one = black.read_cache(1, mode)
            self.assertIn(path, one)
            two = black.read_cache(2, mode)
            self.assertNotIn(path, two)

    def test_single_file_force_pyi(self) -> None:
        reg_mode = black.FileMode.AUTO_DETECT
        pyi_mode = black.FileMode.PYI
        contents, expected = read_data("force_pyi")
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(contents)
            result = CliRunner().invoke(black.main, [str(path), "--pyi"])
            self.assertEqual(result.exit_code, 0)
            with open(path, "r") as fh:
                actual = fh.read()
            # verify cache with --pyi is separate
            pyi_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, pyi_mode)
            self.assertIn(path, pyi_cache)
            normal_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, reg_mode)
            self.assertNotIn(path, normal_cache)
        self.assertEqual(actual, expected)

    @event_loop(close=False)
    def test_multi_file_force_pyi(self) -> None:
        reg_mode = black.FileMode.AUTO_DETECT
        pyi_mode = black.FileMode.PYI
        contents, expected = read_data("force_pyi")
        with cache_dir() as workspace:
            paths = [
                (workspace / "file1.py").resolve(),
                (workspace / "file2.py").resolve(),
            ]
            for path in paths:
                with open(path, "w") as fh:
                    fh.write(contents)
            result = CliRunner().invoke(black.main, [str(p) for p in paths] + ["--pyi"])
            self.assertEqual(result.exit_code, 0)
            for path in paths:
                with open(path, "r") as fh:
                    actual = fh.read()
                self.assertEqual(actual, expected)
            # verify cache with --pyi is separate
            pyi_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, pyi_mode)
            normal_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, reg_mode)
            for path in paths:
                self.assertIn(path, pyi_cache)
                self.assertNotIn(path, normal_cache)

    def test_pipe_force_pyi(self) -> None:
        source, expected = read_data("force_pyi")
        result = CliRunner().invoke(black.main, ["-", "-q", "--pyi"], input=source)
        self.assertEqual(result.exit_code, 0)
        actual = result.output
        self.assertFormatEqual(actual, expected)

    def test_single_file_force_py36(self) -> None:
        reg_mode = black.FileMode.AUTO_DETECT
        py36_mode = black.FileMode.PYTHON36
        source, expected = read_data("force_py36")
        with cache_dir() as workspace:
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(source)
            result = CliRunner().invoke(black.main, [str(path), "--py36"])
            self.assertEqual(result.exit_code, 0)
            with open(path, "r") as fh:
                actual = fh.read()
            # verify cache with --py36 is separate
            py36_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, py36_mode)
            self.assertIn(path, py36_cache)
            normal_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, reg_mode)
            self.assertNotIn(path, normal_cache)
        self.assertEqual(actual, expected)

    @event_loop(close=False)
    def test_multi_file_force_py36(self) -> None:
        reg_mode = black.FileMode.AUTO_DETECT
        py36_mode = black.FileMode.PYTHON36
        source, expected = read_data("force_py36")
        with cache_dir() as workspace:
            paths = [
                (workspace / "file1.py").resolve(),
                (workspace / "file2.py").resolve(),
            ]
            for path in paths:
                with open(path, "w") as fh:
                    fh.write(source)
            result = CliRunner().invoke(
                black.main, [str(p) for p in paths] + ["--py36"]
            )
            self.assertEqual(result.exit_code, 0)
            for path in paths:
                with open(path, "r") as fh:
                    actual = fh.read()
                self.assertEqual(actual, expected)
            # verify cache with --py36 is separate
            pyi_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, py36_mode)
            normal_cache = black.read_cache(black.DEFAULT_LINE_LENGTH, reg_mode)
            for path in paths:
                self.assertIn(path, pyi_cache)
                self.assertNotIn(path, normal_cache)

    def test_pipe_force_py36(self) -> None:
        source, expected = read_data("force_py36")
        result = CliRunner().invoke(black.main, ["-", "-q", "--py36"], input=source)
        self.assertEqual(result.exit_code, 0)
        actual = result.output
        self.assertFormatEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
