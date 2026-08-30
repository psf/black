# flags: --unstable
my_dict = {
    "key": (
        "A very very very very very very very very very very very very very very very very long string literal"
    )  # type: ignore
}

# output

my_dict = {
    "key": (
        "A very very very very very very very very very very very very very very very"
        " very long string literal"
    )  # type: ignore
}
