a = (
    1 +  # type: ignore
    2  # type: ignore
)
a = (
    1  # type: ignore
    + 2  # type: ignore
)
bad_split3 = (
    "What if we have inline comments on "  # First Comment
    "each line of a bad split? In that "  # Second Comment
    "case, we should just leave it alone."  # Third Comment
)
parametrize(
    (
        {},
        {},
    ),
    (  # foobar
        {},
        {},
    ),
)
parser.add_argument("--retries",  # 0 disables
                    help="Number of times to retry "
                         "before giving up")
def check(path):
    if not path.exists():
        raise FileNotFoundError(errno.ENOENT,  # keep errno
                                "Config file is missing: "
                                "run init")
call(
    "aaaaaaaaaaaaaaaaaaaa",
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"  # comment
    "ccccccccccccccccccccccccccccccc",
)



# output
a = (
    1  # type: ignore
    + 2  # type: ignore
)
a = (
    1  # type: ignore
    + 2  # type: ignore
)
bad_split3 = (
    "What if we have inline comments on "  # First Comment
    "each line of a bad split? In that "  # Second Comment
    "case, we should just leave it alone."  # Third Comment
)
parametrize(
    (
        {},
        {},
    ),
    (  # foobar
        {},
        {},
    ),
)
parser.add_argument(
    "--retries",  # 0 disables
    help="Number of times to retry " "before giving up",
)


def check(path):
    if not path.exists():
        raise FileNotFoundError(
            errno.ENOENT,  # keep errno
            "Config file is missing: " "run init",
        )


call(
    "aaaaaaaaaaaaaaaaaaaa",
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"  # comment
    "ccccccccccccccccccccccccccccccc",
)

