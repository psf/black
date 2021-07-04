from black import NothingChanged, format_cell, format_ipynb_string
import os
from tests.util import DEFAULT_MODE
import pytest

pytest.importorskip("IPython")


def test_noop() -> None:
    src = 'foo = "a"'
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_trailing_semicolon() -> None:
    src = 'foo = "a" ;'
    result = format_cell(src, mode=DEFAULT_MODE)
    expected = 'foo = "a";'
    assert result == expected


def test_trailing_semicolon_noop() -> None:
    src = 'foo = "a";'
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_cell_magic() -> None:
    src = "%%time\nfoo =bar"
    result = format_cell(src, mode=DEFAULT_MODE)
    expected = "%%time\nfoo = bar"
    assert result == expected


def test_cell_magic_noop() -> None:
    src = "%%time\n2 + 2"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


@pytest.mark.parametrize(
    "src, expected",
    (
        pytest.param("ls =!ls", "ls = !ls", id="System assignment"),
        pytest.param("!ls\n'foo'", '!ls\n"foo"', id="System call"),
        pytest.param("!!ls\n'foo'", '!!ls\n"foo"', id="Other system call"),
        pytest.param("?str\n'foo'", '?str\n"foo"', id="Help"),
        pytest.param("??str\n'foo'", '??str\n"foo"', id="Other help"),
        pytest.param(
            "%matplotlib inline\n'foo'",
            '%matplotlib inline\n"foo"',
            id="Line magic with argument",
        ),
        pytest.param("%time\n'foo'", '%time\n"foo"', id="Line magic without argument"),
    ),
)
def test_magic(src: str, expected: str) -> None:
    result = format_cell(src, mode=DEFAULT_MODE)
    assert result == expected


def test_set_input() -> None:
    src = "a = b??"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_magic_noop() -> None:
    src = "ls = !ls"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_cell_magic_with_magic() -> None:
    src = "%%t -n1\nls =!ls"
    result = format_cell(src, mode=DEFAULT_MODE)
    expected = "%%t -n1\nls = !ls"
    assert result == expected


def test_cell_magic_nested() -> None:
    src = "%%time\n%%time\n2+2"
    result = format_cell(src, mode=DEFAULT_MODE)
    expected = "%%time\n%%time\n2 + 2"
    assert result == expected


def test_cell_magic_with_magic_noop() -> None:
    src = "%%t -n1\nls = !ls"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_automagic() -> None:
    src = "pip install black"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_multiline_magic() -> None:
    src = "%time 1 + \\\n2"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_multiline_no_magic() -> None:
    src = "1 + \\\n2"
    result = format_cell(src, mode=DEFAULT_MODE)
    expected = "1 + 2"
    assert result == expected


def test_cell_magic_with_invalid_body() -> None:
    src = "%%time\nif True"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_empty_cell() -> None:
    src = ""
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_entire_notebook_trailing_newline() -> None:
    with open(
        os.path.join("tests", "data", "notebook_trailing_newline.ipynb"), "rb"
    ) as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    result = format_ipynb_string(content, mode=DEFAULT_MODE)
    expected = (
        "{\n"
        ' "cells": [\n'
        "  {\n"
        '   "cell_type": "code",\n'
        '   "execution_count": null,\n'
        '   "metadata": {\n'
        '    "tags": []\n'
        "   },\n"
        '   "outputs": [],\n'
        '   "source": [\n'
        '    "%%time\\n",\n'
        '    "\\n",\n'
        '    "print(\\"foo\\")"\n'
        "   ]\n"
        "  },\n"
        "  {\n"
        '   "cell_type": "code",\n'
        '   "execution_count": null,\n'
        '   "metadata": {},\n'
        '   "outputs": [],\n'
        '   "source": []\n'
        "  }\n"
        " ],\n"
        ' "metadata": {\n'
        '  "interpreter": {\n'
        '   "hash": "e758f3098b5b55f4d87fe30bbdc1367f20f246b483f96267ee70e6c40cb185d8"\n'  # noqa:B950
        "  },\n"
        '  "kernelspec": {\n'
        '   "display_name": "Python 3.8.10 64-bit (\'black\': venv)",\n'
        '   "name": "python3"\n'
        "  },\n"
        '  "language_info": {\n'
        '   "name": "python",\n'
        '   "version": ""\n'
        "  }\n"
        " },\n"
        ' "nbformat": 4,\n'
        ' "nbformat_minor": 4\n'
        "}\n"
    )
    assert result == expected


def test_entire_notebook_no_trailing_newline() -> None:
    with open(
        os.path.join("tests", "data", "notebook_no_trailing_newline.ipynb"), "rb"
    ) as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    result = format_ipynb_string(content, mode=DEFAULT_MODE)
    expected = (
        "{\n"
        ' "cells": [\n'
        "  {\n"
        '   "cell_type": "code",\n'
        '   "execution_count": null,\n'
        '   "metadata": {\n'
        '    "tags": []\n'
        "   },\n"
        '   "outputs": [],\n'
        '   "source": [\n'
        '    "%%time\\n",\n'
        '    "\\n",\n'
        '    "print(\\"foo\\")"\n'
        "   ]\n"
        "  },\n"
        "  {\n"
        '   "cell_type": "code",\n'
        '   "execution_count": null,\n'
        '   "metadata": {},\n'
        '   "outputs": [],\n'
        '   "source": []\n'
        "  }\n"
        " ],\n"
        ' "metadata": {\n'
        '  "interpreter": {\n'
        '   "hash": "e758f3098b5b55f4d87fe30bbdc1367f20f246b483f96267ee70e6c40cb185d8"\n'  # noqa: B950
        "  },\n"
        '  "kernelspec": {\n'
        '   "display_name": "Python 3.8.10 64-bit (\'black\': venv)",\n'
        '   "name": "python3"\n'
        "  },\n"
        '  "language_info": {\n'
        '   "name": "python",\n'
        '   "version": ""\n'
        "  }\n"
        " },\n"
        ' "nbformat": 4,\n'
        ' "nbformat_minor": 4\n'
        "}"
    )
    assert result == expected


def test_entire_notebook_without_changes() -> None:
    with open(
        os.path.join("tests", "data", "notebook_without_changes.ipynb"), "rb"
    ) as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    with pytest.raises(NothingChanged):
        format_ipynb_string(content, mode=DEFAULT_MODE)


def test_empty_string() -> None:
    with pytest.raises(NothingChanged):
        format_ipynb_string("", mode=DEFAULT_MODE)
