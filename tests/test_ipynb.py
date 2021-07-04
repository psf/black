from black import NothingChanged, format_cell
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


def test_cell_magic_with_magic_noop() -> None:
    src = "%%t -n1\nls = !ls"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_automagic() -> None:
    src = "pip install black"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_cell_magic_with_invalid_body() -> None:
    src = "%%time\nif True"
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_empty_cell() -> None:
    src = ""
    with pytest.raises(NothingChanged):
        format_cell(src, mode=DEFAULT_MODE)


def test_entire_notebook() -> None:
    pass
