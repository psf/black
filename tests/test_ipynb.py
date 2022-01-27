from dataclasses import replace
import pathlib
import re
from contextlib import ExitStack as does_not_raise
from typing import ContextManager

from click.testing import CliRunner
from black.handle_ipynb_magics import jupyter_dependencies_are_installed
from black import (
    main,
    NothingChanged,
    format_cell,
    format_file_contents,
    format_file_in_place,
)
import pytest
from black import Mode
from _pytest.monkeypatch import MonkeyPatch
from tests.util import DATA_DIR

pytestmark = pytest.mark.jupyter
pytest.importorskip("IPython", reason="IPython is an optional dependency")
pytest.importorskip("tokenize_rt", reason="tokenize-rt is an optional dependency")

JUPYTER_MODE = Mode(is_ipynb=True)

runner = CliRunner()


def test_noop() -> None:
    src = 'foo = "a"'
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


@pytest.mark.parametrize("fast", [True, False])
def test_trailing_semicolon(fast: bool) -> None:
    src = 'foo = "a" ;'
    result = format_cell(src, fast=fast, mode=JUPYTER_MODE)
    expected = 'foo = "a";'
    assert result == expected


def test_trailing_semicolon_with_comment() -> None:
    src = 'foo = "a" ;  # bar'
    result = format_cell(src, fast=True, mode=JUPYTER_MODE)
    expected = 'foo = "a";  # bar'
    assert result == expected


def test_trailing_semicolon_with_comment_on_next_line() -> None:
    src = "import black;\n\n# this is a comment"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_trailing_semicolon_indented() -> None:
    src = "with foo:\n    plot_bar();"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_trailing_semicolon_noop() -> None:
    src = 'foo = "a";'
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


@pytest.mark.parametrize(
    "mode",
    [
        pytest.param(JUPYTER_MODE, id="default mode"),
        pytest.param(
            replace(JUPYTER_MODE, python_cell_magics={"cust1", "cust1"}),
            id="custom cell magics mode",
        ),
    ],
)
def test_cell_magic(mode: Mode) -> None:
    src = "%%time\nfoo =bar"
    result = format_cell(src, fast=True, mode=mode)
    expected = "%%time\nfoo = bar"
    assert result == expected


def test_cell_magic_noop() -> None:
    src = "%%time\n2 + 2"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


@pytest.mark.parametrize(
    "mode",
    [
        pytest.param(JUPYTER_MODE, id="default mode"),
        pytest.param(
            replace(JUPYTER_MODE, python_cell_magics={"cust1", "cust1"}),
            id="custom cell magics mode",
        ),
    ],
)
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
        pytest.param(
            "env =  %env var", "env = %env var", id="Assignment to environment variable"
        ),
        pytest.param("env =  %env", "env = %env", id="Assignment to magic"),
    ),
)
def test_magic(src: str, expected: str, mode: Mode) -> None:
    result = format_cell(src, fast=True, mode=mode)
    assert result == expected


@pytest.mark.parametrize(
    "src",
    (
        "%%bash\n2+2",
        "%%html --isolated\n2+2",
        "%%writefile e.txt\n  meh\n meh",
    ),
)
def test_non_python_magics(src: str) -> None:
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_set_input() -> None:
    src = "a = b??"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_input_already_contains_transformed_magic() -> None:
    src = '%time foo()\nget_ipython().run_cell_magic("time", "", "foo()\\n")'
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_magic_noop() -> None:
    src = "ls = !ls"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_cell_magic_with_magic() -> None:
    src = "%%timeit -n1\nls =!ls"
    result = format_cell(src, fast=True, mode=JUPYTER_MODE)
    expected = "%%timeit -n1\nls = !ls"
    assert result == expected


@pytest.mark.parametrize(
    "mode, expected_output, expectation",
    [
        pytest.param(
            JUPYTER_MODE,
            "%%custom_python_magic -n1 -n2\nx=2",
            pytest.raises(NothingChanged),
            id="No change when cell magic not registered",
        ),
        pytest.param(
            replace(JUPYTER_MODE, python_cell_magics={"cust1", "cust1"}),
            "%%custom_python_magic -n1 -n2\nx=2",
            pytest.raises(NothingChanged),
            id="No change when other cell magics registered",
        ),
        pytest.param(
            replace(JUPYTER_MODE, python_cell_magics={"custom_python_magic", "cust1"}),
            "%%custom_python_magic -n1 -n2\nx = 2",
            does_not_raise(),
            id="Correctly change when cell magic registered",
        ),
    ],
)
def test_cell_magic_with_custom_python_magic(
    mode: Mode, expected_output: str, expectation: ContextManager[object]
) -> None:
    with expectation:
        result = format_cell(
            "%%custom_python_magic -n1 -n2\nx=2",
            fast=True,
            mode=mode,
        )
        assert result == expected_output


def test_cell_magic_nested() -> None:
    src = "%%time\n%%time\n2+2"
    result = format_cell(src, fast=True, mode=JUPYTER_MODE)
    expected = "%%time\n%%time\n2 + 2"
    assert result == expected


def test_cell_magic_with_magic_noop() -> None:
    src = "%%t -n1\nls = !ls"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_automagic() -> None:
    src = "pip install black"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_multiline_magic() -> None:
    src = "%time 1 + \\\n2"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_multiline_no_magic() -> None:
    src = "1 + \\\n2"
    result = format_cell(src, fast=True, mode=JUPYTER_MODE)
    expected = "1 + 2"
    assert result == expected


def test_cell_magic_with_invalid_body() -> None:
    src = "%%time\nif True"
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_empty_cell() -> None:
    src = ""
    with pytest.raises(NothingChanged):
        format_cell(src, fast=True, mode=JUPYTER_MODE)


def test_entire_notebook_empty_metadata() -> None:
    with open(DATA_DIR / "notebook_empty_metadata.ipynb", "rb") as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    result = format_file_contents(content, fast=True, mode=JUPYTER_MODE)
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
        ' "metadata": {},\n'
        ' "nbformat": 4,\n'
        ' "nbformat_minor": 4\n'
        "}\n"
    )
    assert result == expected


def test_entire_notebook_trailing_newline() -> None:
    with open(DATA_DIR / "notebook_trailing_newline.ipynb", "rb") as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    result = format_file_contents(content, fast=True, mode=JUPYTER_MODE)
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
    with open(DATA_DIR / "notebook_no_trailing_newline.ipynb", "rb") as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    result = format_file_contents(content, fast=True, mode=JUPYTER_MODE)
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
    with open(DATA_DIR / "notebook_without_changes.ipynb", "rb") as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    with pytest.raises(NothingChanged):
        format_file_contents(content, fast=True, mode=JUPYTER_MODE)


def test_non_python_notebook() -> None:
    with open(DATA_DIR / "non_python_notebook.ipynb", "rb") as fd:
        content_bytes = fd.read()
    content = content_bytes.decode()
    with pytest.raises(NothingChanged):
        format_file_contents(content, fast=True, mode=JUPYTER_MODE)


def test_empty_string() -> None:
    with pytest.raises(NothingChanged):
        format_file_contents("", fast=True, mode=JUPYTER_MODE)


def test_unparseable_notebook() -> None:
    path = DATA_DIR / "notebook_which_cant_be_parsed.ipynb"
    msg = rf"File '{re.escape(str(path))}' cannot be parsed as valid Jupyter notebook\."
    with pytest.raises(ValueError, match=msg):
        format_file_in_place(path, fast=True, mode=JUPYTER_MODE)


def test_ipynb_diff_with_change() -> None:
    result = runner.invoke(
        main,
        [
            str(DATA_DIR / "notebook_trailing_newline.ipynb"),
            "--diff",
        ],
    )
    expected = "@@ -1,3 +1,3 @@\n %%time\n \n-print('foo')\n" '+print("foo")\n'
    assert expected in result.output


def test_ipynb_diff_with_no_change() -> None:
    result = runner.invoke(
        main,
        [
            str(DATA_DIR / "notebook_without_changes.ipynb"),
            "--diff",
        ],
    )
    expected = "1 file would be left unchanged."
    assert expected in result.output


def test_cache_isnt_written_if_no_jupyter_deps_single(
    monkeypatch: MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    # Check that the cache isn't written to if Jupyter dependencies aren't installed.
    jupyter_dependencies_are_installed.cache_clear()
    nb = DATA_DIR / "notebook_trailing_newline.ipynb"
    tmp_nb = tmp_path / "notebook.ipynb"
    with open(nb) as src, open(tmp_nb, "w") as dst:
        dst.write(src.read())
    monkeypatch.setattr(
        "black.jupyter_dependencies_are_installed", lambda verbose, quiet: False
    )
    result = runner.invoke(main, [str(tmp_path / "notebook.ipynb")])
    assert "No Python files are present to be formatted. Nothing to do" in result.output
    jupyter_dependencies_are_installed.cache_clear()
    monkeypatch.setattr(
        "black.jupyter_dependencies_are_installed", lambda verbose, quiet: True
    )
    result = runner.invoke(main, [str(tmp_path / "notebook.ipynb")])
    assert "reformatted" in result.output


def test_cache_isnt_written_if_no_jupyter_deps_dir(
    monkeypatch: MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    # Check that the cache isn't written to if Jupyter dependencies aren't installed.
    jupyter_dependencies_are_installed.cache_clear()
    nb = DATA_DIR / "notebook_trailing_newline.ipynb"
    tmp_nb = tmp_path / "notebook.ipynb"
    with open(nb) as src, open(tmp_nb, "w") as dst:
        dst.write(src.read())
    monkeypatch.setattr(
        "black.files.jupyter_dependencies_are_installed", lambda verbose, quiet: False
    )
    result = runner.invoke(main, [str(tmp_path)])
    assert "No Python files are present to be formatted. Nothing to do" in result.output
    jupyter_dependencies_are_installed.cache_clear()
    monkeypatch.setattr(
        "black.files.jupyter_dependencies_are_installed", lambda verbose, quiet: True
    )
    result = runner.invoke(main, [str(tmp_path)])
    assert "reformatted" in result.output


def test_ipynb_flag(tmp_path: pathlib.Path) -> None:
    nb = DATA_DIR / "notebook_trailing_newline.ipynb"
    tmp_nb = tmp_path / "notebook.a_file_extension_which_is_definitely_not_ipynb"
    with open(nb) as src, open(tmp_nb, "w") as dst:
        dst.write(src.read())
    result = runner.invoke(
        main,
        [
            str(tmp_nb),
            "--diff",
            "--ipynb",
        ],
    )
    expected = "@@ -1,3 +1,3 @@\n %%time\n \n-print('foo')\n" '+print("foo")\n'
    assert expected in result.output


def test_ipynb_and_pyi_flags() -> None:
    nb = DATA_DIR / "notebook_trailing_newline.ipynb"
    result = runner.invoke(
        main,
        [
            str(nb),
            "--pyi",
            "--ipynb",
            "--diff",
        ],
    )
    assert isinstance(result.exception, SystemExit)
    expected = "Cannot pass both `pyi` and `ipynb` flags!\n"
    assert result.output == expected


def test_unable_to_replace_magics(monkeypatch: MonkeyPatch) -> None:
    src = "%%time\na = 'foo'"
    monkeypatch.setattr("black.handle_ipynb_magics.TOKEN_HEX", lambda _: "foo")
    with pytest.raises(
        AssertionError, match="Black was not able to replace IPython magic"
    ):
        format_cell(src, fast=True, mode=JUPYTER_MODE)
