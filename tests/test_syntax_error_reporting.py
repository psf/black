from pathlib import Path

import pytest
from click.testing import CliRunner

import black


def test_syntax_error_reporting(tmp_path):
    src = tmp_path / "bad_syntax.py"
    src.write_text("def my_func()\n    pass", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(black.main, [str(src)])

    assert result.exit_code == 123
    assert "Error: Cannot parse" in result.output
    assert "black's parser found a syntax error on or near line 1" in result.output
    assert 'File "' in result.output
    assert ', line 1:' in result.output
    assert "def my_func()" in result.output
    assert "^" in result.output
