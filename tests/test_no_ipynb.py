import pathlib

import pytest
from click.testing import CliRunner

from black import jupyter_dependencies_are_installed, main
from tests.util import get_case_path

pytestmark = pytest.mark.no_jupyter

runner = CliRunner()


def test_ipynb_diff_with_no_change_single() -> None:
    jupyter_dependencies_are_installed.cache_clear()
    path = get_case_path("jupyter", "notebook_trailing_newline.ipynb")
    result = runner.invoke(main, [str(path)])
    expected_output = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        'You can fix this by running ``pip install "black[jupyter]"``\n'
    )
    assert expected_output in result.output


def test_ipynb_diff_with_no_change_dir(tmp_path: pathlib.Path) -> None:
    jupyter_dependencies_are_installed.cache_clear()
    runner = CliRunner()
    nb = get_case_path("jupyter", "notebook_trailing_newline.ipynb")
    tmp_nb = tmp_path / "notebook.ipynb"
    tmp_nb.write_bytes(nb.read_bytes())
    result = runner.invoke(main, [str(tmp_path)])
    expected_output = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        'You can fix this by running ``pip install "black[jupyter]"``\n'
    )
    assert expected_output in result.output
