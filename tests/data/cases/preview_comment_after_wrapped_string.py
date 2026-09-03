# flags: --unstable
# Regression test for https://github.com/psf/black/issues/3802
def __str__(self):
    return "foo bar baz qux" # pyright: ignore[reportGeneralTypeIssues] -- This is some special Django magic that we can't easily tell Pyright about


# output


# Regression test for https://github.com/psf/black/issues/3802
def __str__(self):
    return (
        "foo bar baz qux"  # pyright: ignore[reportGeneralTypeIssues] -- This is some special Django magic that we can't easily tell Pyright about
    )
