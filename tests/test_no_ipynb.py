from tests.util import DEFAULT_MODE
import pytest
from black import WriteBack, format_file_in_place

from tests.util import THIS_DIR

pytestmark = pytest.mark.no_jupyter


def test_ipynb_diff_with_no_change() -> None:
    path = THIS_DIR / "data/notebook_trailing_newline.ipynb"
    msg = r"Skipping '.*' as IPython is not installed."
    with pytest.warns(UserWarning, match=msg):
        format_file_in_place(
            path, fast=False, mode=DEFAULT_MODE, write_back=WriteBack.DIFF
        )
