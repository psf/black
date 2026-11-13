parser.add_argument(
    "--foo",
    default=  # keep in sync with bar
        DEFAULT_FOO,  # type: ignore[arg-type]
)

foo(
    **  # extra options
    kwargs,  # type: ignore[arg-type]
)

settings = {
    "timeout":  # seconds
        timeout,  # type: ignore[dict-item]
}


def build(
    prefix: str =  # relative to the root
        DEFAULT_PREFIX,  # type: ignore[assignment]
):
    pass


# output
parser.add_argument(
    "--foo",
    default=DEFAULT_FOO,  # type: ignore[arg-type]  # keep in sync with bar
)

foo(
    **kwargs,  # type: ignore[arg-type]  # extra options
)

settings = {
    "timeout": timeout,  # type: ignore[dict-item]  # seconds
}


def build(
    prefix: str = DEFAULT_PREFIX,  # type: ignore[assignment]  # relative to the root
):
    pass
