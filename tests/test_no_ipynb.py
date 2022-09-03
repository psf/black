import pathlib

import pytest
from click.testing import CliRunner

from black import jupyter_dependencies_are_installed, main
from tests.util import get_case_path
from unittest.mock import patch

pytestmark = pytest.mark.no_jupyter

runner = CliRunner()


@patch("platform.platform")
def test_ipynb_diff_with_no_change_single_on_linux(platform_platform) -> None:
    platform_platform.return_value = "some-linux-distro-v0.1.2"
    jupyter_dependencies_are_installed.cache_clear()
    path = get_case_path("jupyter", "notebook_trailing_newline.ipynb")
    result = runner.invoke(main, [str(path)])
    expected_output = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        "You can fix this by running ``pip install 'black[jupyter]'``\n"
    )
    assert expected_output in result.output


@patch("platform.platform")
def test_ipynb_diff_with_no_change_single_not_linux(platform_platform) -> None:
    platform_platform.return_value = "windows-or-mac-etc"
    jupyter_dependencies_are_installed.cache_clear()
    path = get_case_path("jupyter", "notebook_trailing_newline.ipynb")
    result = runner.invoke(main, [str(path)])
    expected_output = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        "You can fix this by running ``pip install black[jupyter]``\n"
    )
    assert expected_output in result.output


@patch("platform.platform")
def test_ipynb_diff_with_no_change_dir_on_linux(
    platform_platform, tmp_path: pathlib.Path
) -> None:
    platform_platform.return_value = "some-linux-distro-v0.1.2"
    jupyter_dependencies_are_installed.cache_clear()
    runner = CliRunner()
    nb = get_case_path("jupyter", "notebook_trailing_newline.ipynb")
    tmp_nb = tmp_path / "notebook.ipynb"
    with open(nb) as src, open(tmp_nb, "w") as dst:
        dst.write(src.read())
    result = runner.invoke(main, [str(tmp_path)])
    expected_output = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        "You can fix this by running ``pip install 'black[jupyter]'``\n"
    )
    assert expected_output in result.output


@patch("platform.platform")
def test_ipynb_diff_with_no_change_dir_not_linux(
    platform_platform, tmp_path: pathlib.Path
) -> None:
    platform_platform.return_value = "windows-or-mac-etc"
    jupyter_dependencies_are_installed.cache_clear()
    runner = CliRunner()
    nb = get_case_path("jupyter", "notebook_trailing_newline.ipynb")
    tmp_nb = tmp_path / "notebook.ipynb"
    with open(nb) as src, open(tmp_nb, "w") as dst:
        dst.write(src.read())
    result = runner.invoke(main, [str(tmp_path)])
    expected_output = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        "You can fix this by running ``pip install black[jupyter]``\n"
    )
    assert expected_output in result.output
