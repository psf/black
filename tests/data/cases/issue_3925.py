# flags: --preview --line-length=24

abcdefghij = (
    abcdefgh
    + (
        # comment
        abcdefghijkl
        + abcdefghijkl
    )
)


def returns_value():
    return (
        abcdefghijkl
        + (
            # comment
            abcdefghijkl
            + abcdefghijkl
        )
    )


def checks_value():
    assert (
        abcdefghijkl
        + (
            # comment
            abcdefghijkl
            + abcdefghijkl
        )
    )


def yields_value():
    yield (
        abcdefghijkl
        + (
            # comment
            abcdefghijkl
            + abcdefghijkl
        )
    )

# output
abcdefghij = (
    abcdefgh
    + (
        # comment
        abcdefghijkl
        + abcdefghijkl
    )
)


def returns_value():
    return (
        abcdefghijkl
        + (
            # comment
            abcdefghijkl
            + abcdefghijkl
        )
    )


def checks_value():
    assert (
        abcdefghijkl
        + (
            # comment
            abcdefghijkl
            + abcdefghijkl
        )
    )


def yields_value():
    yield (
        abcdefghijkl
        + (
            # comment
            abcdefghijkl
            + abcdefghijkl
        )
    )
