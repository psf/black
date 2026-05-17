# Regression test for https://github.com/psf/black/issues/4733.
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa: list[  # bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
    int
] = []


# Original (non-minimized) snippet from the issue report.
def foo():
    possibly_redundant_lowlevel_checkpoints: list[  # pyright: ignore[reportUnknownVariableType]
        cst.BaseExpression
    ] = field( default_factory=list)

# output

# Regression test for https://github.com/psf/black/issues/4733.
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa: list[  # bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
    int
] = []


# Original (non-minimized) snippet from the issue report.
def foo():
    possibly_redundant_lowlevel_checkpoints: list[  # pyright: ignore[reportUnknownVariableType]
        cst.BaseExpression
    ] = field(default_factory=list)
