#!/usr/bin/env python3
from functools import partial
from io import StringIO
from pathlib import Path
import sys
from typing import Any, List, Tuple
import unittest
from unittest.mock import patch

from click import unstyle

import black

ll = 88
ff = partial(black.format_file_in_place, line_length=ll, fast=True)
fs = partial(black.format_str, line_length=ll)
THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent


def dump_to_stderr(*output: str) -> str:
    return '\n' + '\n'.join(output) + '\n'


def read_data(name: str) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    if not name.endswith('.py'):
        name += '.py'
    _input: List[str] = []
    _output: List[str] = []
    with open(THIS_DIR / name, 'r', encoding='utf8') as test:
        lines = test.readlines()
    result = _input
    for line in lines:
        if line.rstrip() == '# output':
            result = _output
            continue

        result.append(line)
    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return ''.join(_input).strip() + '\n', ''.join(_output).strip() + '\n'


class BlackTestCase(unittest.TestCase):
    maxDiff = None

    def assertFormatEqual(self, expected: str, actual: str) -> None:
        if actual != expected:
            bdv: black.DebugVisitor[Any]
            black.out('Expected tree:', fg='green')
            try:
                exp_node = black.lib2to3_parse(expected)
                bdv = black.DebugVisitor()
                list(bdv.visit(exp_node))
            except Exception as ve:
                black.err(str(ve))
            black.out('Actual tree:', fg='red')
            try:
                exp_node = black.lib2to3_parse(actual)
                bdv = black.DebugVisitor()
                list(bdv.visit(exp_node))
            except Exception as ve:
                black.err(str(ve))
        self.assertEqual(expected, actual)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_self(self) -> None:
        source, expected = read_data('test_black')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)
        self.assertFalse(ff(THIS_FILE))

    @patch("black.dump_to_file", dump_to_stderr)
    def test_black(self) -> None:
        source, expected = read_data('../black')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)
        self.assertFalse(ff(THIS_DIR / '..' / 'black.py'))

    def test_piping(self) -> None:
        source, expected = read_data('../black')
        hold_stdin, hold_stdout = sys.stdin, sys.stdout
        try:
            sys.stdin, sys.stdout = StringIO(source), StringIO()
            sys.stdin.name = '<stdin>'
            black.format_stdin_to_stdout(line_length=ll, fast=True)
            sys.stdout.seek(0)
            actual = sys.stdout.read()
        finally:
            sys.stdin, sys.stdout = hold_stdin, hold_stdout
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_setup(self) -> None:
        source, expected = read_data('../setup')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)
        self.assertFalse(ff(THIS_DIR / '..' / 'setup.py'))

    @patch("black.dump_to_file", dump_to_stderr)
    def test_function(self) -> None:
        source, expected = read_data('function')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_expression(self) -> None:
        source, expected = read_data('expression')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_fstring(self) -> None:
        source, expected = read_data('fstring')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_comments(self) -> None:
        source, expected = read_data('comments')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_comments2(self) -> None:
        source, expected = read_data('comments2')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_cantfit(self) -> None:
        source, expected = read_data('cantfit')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_import_spacing(self) -> None:
        source, expected = read_data('import_spacing')
        actual = fs(source)
        self.assertFormatEqual(expected, actual)
        black.assert_equivalent(source, actual)
        black.assert_stable(source, actual, line_length=ll)

    @patch("black.dump_to_file", dump_to_stderr)
    def test_composition(self) -> None:
        source, expected = read_data('composition')
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
            report.done(Path('f1'), changed=False)
            self.assertEqual(len(out_lines), 1)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], 'f1 already well formatted, good job.')
            self.assertEqual(unstyle(str(report)), '1 file left unchanged.')
            self.assertEqual(report.return_code, 0)
            report.done(Path('f2'), changed=True)
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 0)
            self.assertEqual(out_lines[-1], 'reformatted f2')
            self.assertEqual(
                unstyle(str(report)), '1 file reformatted, 1 file left unchanged.'
            )
            self.assertEqual(report.return_code, 1)
            report.failed(Path('e1'), 'boom')
            self.assertEqual(len(out_lines), 2)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(err_lines[-1], 'error: cannot format e1: boom')
            self.assertEqual(
                unstyle(str(report)),
                '1 file reformatted, 1 file left unchanged, '
                '1 file failed to reformat.',
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path('f3'), changed=True)
            self.assertEqual(len(out_lines), 3)
            self.assertEqual(len(err_lines), 1)
            self.assertEqual(out_lines[-1], 'reformatted f3')
            self.assertEqual(
                unstyle(str(report)),
                '2 files reformatted, 1 file left unchanged, '
                '1 file failed to reformat.',
            )
            self.assertEqual(report.return_code, 123)
            report.failed(Path('e2'), 'boom')
            self.assertEqual(len(out_lines), 3)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(err_lines[-1], 'error: cannot format e2: boom')
            self.assertEqual(
                unstyle(str(report)),
                '2 files reformatted, 1 file left unchanged, '
                '2 files failed to reformat.',
            )
            self.assertEqual(report.return_code, 123)
            report.done(Path('f4'), changed=False)
            self.assertEqual(len(out_lines), 4)
            self.assertEqual(len(err_lines), 2)
            self.assertEqual(out_lines[-1], 'f4 already well formatted, good job.')
            self.assertEqual(
                unstyle(str(report)),
                '2 files reformatted, 2 files left unchanged, '
                '2 files failed to reformat.',
            )
            self.assertEqual(report.return_code, 123)

    def test_is_python36(self) -> None:
        node = black.lib2to3_parse("def f(*, arg): ...\n")
        self.assertFalse(black.is_python36(node))
        node = black.lib2to3_parse("def f(*, arg,): ...\n")
        self.assertTrue(black.is_python36(node))
        node = black.lib2to3_parse("def f(*, arg): f'string'\n")
        self.assertTrue(black.is_python36(node))
        source, expected = read_data('function')
        node = black.lib2to3_parse(source)
        self.assertTrue(black.is_python36(node))
        node = black.lib2to3_parse(expected)
        self.assertTrue(black.is_python36(node))
        source, expected = read_data('expression')
        node = black.lib2to3_parse(source)
        self.assertFalse(black.is_python36(node))
        node = black.lib2to3_parse(expected)
        self.assertFalse(black.is_python36(node))


if __name__ == '__main__':
    unittest.main()
