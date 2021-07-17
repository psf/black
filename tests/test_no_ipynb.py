import subprocess
import pytest

from tests.util import THIS_DIR

pytestmark = pytest.mark.no_jupyter


def test_ipynb_diff_with_no_change() -> None:
    path = THIS_DIR / "data/notebook_trailing_newline.ipynb"
    output = subprocess.run(
        ["black", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    expected_stderr = (
        "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
        "You can fix this by running ``pip install black[jupyter]``\n"
    )
    result_stderr = output.stderr
    assert expected_stderr in result_stderr
