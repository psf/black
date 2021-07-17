import pytest

from tests.util import THIS_DIR
from black import main
from click.testing import CliRunner

pytestmark = pytest.mark.no_jupyter


def test_ipynb_diff_with_no_change() -> None:
    runner = CliRunner()
    path = THIS_DIR / "data/notebook_trailing_newline.ipynb"
    result = runner.invoke(main, [str(path)])
    expected_output = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        "You can fix this by running ``pip install black[jupyter]``\n"
    )
    assert expected_output in result.output
