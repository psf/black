# flags: --skip-magic-trailing-comma
# Regression test for https://github.com/psf/black/issues/4026.

fraction = [
    # comment
    23 / 7,
]

# output
# Regression test for https://github.com/psf/black/issues/4026.

fraction = [
    # comment
    23 / 7
]
