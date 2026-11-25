# flags: --unstable
# Regression test for https://github.com/psf/black/issues/3802.
class A:
    def __str__(self):
        return "foo bar baz qux"  # pyright: ignore[reportGeneralTypeIssues] -- This is some special Django magic that we can't easily tell Pyright about


class B:
    def __str__(self):
        return (
            "foo bar baz qux"  # pyright: ignore[reportGeneralTypeIssues] -- This is some special Django magic that we can't easily tell Pyright about
        )


x = "short string"  # pyright: ignore[reportGeneralTypeIssues] -- this trailing comment is long enough to push the line over the limit


# output
# Regression test for https://github.com/psf/black/issues/3802.
class A:
    def __str__(self):
        return "foo bar baz qux"  # pyright: ignore[reportGeneralTypeIssues] -- This is some special Django magic that we can't easily tell Pyright about


class B:
    def __str__(self):
        return "foo bar baz qux"  # pyright: ignore[reportGeneralTypeIssues] -- This is some special Django magic that we can't easily tell Pyright about


x = "short string"  # pyright: ignore[reportGeneralTypeIssues] -- this trailing comment is long enough to push the line over the limit
