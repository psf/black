"""Regression tests pinning known Black bugs around PEP 695 type parameters.

Each test here asserts the *desired* (correct) behavior and is marked
``xfail(strict=True)``. While the bug is present the test xfails; once the bug is
fixed the assertion starts passing, the strict marker turns that into a failure, and
whoever fixed it is prompted to promote the case into ``tests/data/cases/`` and drop
the marker.
"""

import pytest

import black

MODE = black.Mode(target_versions={black.TargetVersion.PY312})


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Black bug: a magic trailing comma fails to explode a type-parameter list "
        "once it contains a *TypeVarTuple or **ParamSpec. A plain `[T, U,]` explodes "
        "one-per-line, but `[*Ts, **P,]` collapses onto a single line. "
        "See https://github.com/psf/black/issues/5243."
    ),
)
def test_magic_trailing_comma_explodes_starred_type_params() -> None:
    # The magic trailing comma should keep each type parameter on its own line,
    # exactly as it does for plain type vars.
    source = "class C[\n    T,\n    *Ts,\n    **P,\n]:\n    pass\n"
    assert black.format_str(source, mode=MODE) == source
