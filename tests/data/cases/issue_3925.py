# flags: --preview --line-length=24

abcdefghij = (
    abcdefgh
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
