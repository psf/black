import pytest

from black import Mode, format_file_contents, format_markdown_string, NothingChanged
from tests.util import DATA_DIR

MARKDOWN_MODE = Mode(is_markdown=True)


def get_markdown_data(formatted=False):
    with open(
        DATA_DIR / "markdown.md"
        if formatted
        else DATA_DIR / "markdown_without_changes.md",
        "r",
    ) as fd:
        return fd.read()


def test_empty():
    content = ""
    with pytest.raises(NothingChanged):
        format_file_contents(content, fast=True, mode=MARKDOWN_MODE)


def test_markdown_without_code_blocks():
    with open(DATA_DIR / "markdown_without_code.md", "r") as fd:
        content = fd.read()
        with pytest.raises(NothingChanged):
            format_file_contents(content, fast=True, mode=MARKDOWN_MODE)


def test_markdown_code_blocks():
    content = get_markdown_data()
    result = format_file_contents(content, fast=True, mode=MARKDOWN_MODE)
    expected = get_markdown_data(True)
    assert result == expected
