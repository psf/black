# Regression test for https://github.com/psf/black/issues/2877.
# Blank lines that terminate a `# fmt: off` region are inside the region, so
# they must be preserved rather than collapsed to the usual maximum.
x = 1
# fmt: off
a = 1



# fmt: on
y = 2


def f():
    x = 1
    # fmt: off
    a = 1




    # fmt: on
    y = 2


# yapf: disable
b = 1



# yapf: enable
z = 2


# fmt:off
c = 1


# fmt:on
w = 2
