import pytest
from black import Mode, format_str


def test_fmt_off_with_magic_comment_prefix():
    source = """# %% [markdown]
# fmt: off
x = 1
# fmt: on
"""
    expected = """# %% [markdown]
# fmt: off
x = 1
# fmt: on
"""
    mode = Mode()
    assert format_str(source, mode=mode) == expected


def test_fmt_off_with_magic_comment_prefix_indented():
    source = """if True:
    # %% [markdown]
    # fmt: off
    x = 1
    # fmt: on
"""
    expected = """if True:
    # %% [markdown]
    # fmt: off
    x = 1
    # fmt: on
"""
    mode = Mode()
    assert format_str(source, mode=mode) == expected


def test_fmt_off_with_comment_prefix():
    source = """# comment 1
# fmt: off
x = 1
# fmt: on
"""
    expected = """# comment 1
# fmt: off
x = 1
# fmt: on
"""
    mode = Mode()
    assert format_str(source, mode=mode) == expected
