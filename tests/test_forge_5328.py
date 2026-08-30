"""Regression test for issue #5328.

Formatting a dictionary with a long string and a ``# type: ignore`` comment
crashes with INTERNAL ERROR when ``--unstable`` is used because the
``# type: ignore`` comment disappears from the output, making it
non-equivalent to the source.
"""

import black
from black.mode import Mode


def test_type_ignore_preserved_with_unstable() -> None:
    src = '''my_dict = {
    "key": (
        "A very very very very very very very very very very very very very very very very long string literal"
    )  # type: ignore
}
'''
    mode = Mode(unstable=True)
    dst = black.format_str(src, mode=mode)
    # The type: ignore comment must survive formatting.
    assert "# type: ignore" in dst
    # And the output must be equivalent to the source.
    black.assert_equivalent(src, dst)