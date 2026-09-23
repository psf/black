# Regression test for https://github.com/psf/black/issues/5397.
if (  # fmt: skip
    True
):  # fmt: skip
    pass

if (
    a in (  # fmt: skip
        1,
    )  # fmt: skip
):  # fmt: skip
    pass

if (
    a in (  # fmt: skip
        1,
    )  #  fmt:skip
):  # fmt: skip
    pass

if (
    a in (  # fmt: skip
        1,
    )  # foobar # fmt:skip
):  # fmt: skip
    pass

# output

# Regression test for https://github.com/psf/black/issues/5397.
if (  # fmt: skip
    True
):  # fmt: skip
    pass

if (
    a in (  # fmt: skip
        1,
    )  # fmt: skip
):  # fmt: skip
    pass

if (
    a in (  # fmt: skip
        1,
    )  #  fmt:skip
):  # fmt: skip
    pass

if (
    a in (  # fmt: skip
        1,
    )  # foobar # fmt:skip
):  # fmt: skip
    pass
