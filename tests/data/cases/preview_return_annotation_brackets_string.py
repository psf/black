# flags: --unstable
# Long string example
def frobnicate() -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# split the string even when there are parameters
def frobnicate(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# don't split strings followed by pragmas
def with_type_ignore(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # type: ignore
    pass

def with_fmt_skip(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # fmt: skip
    pass

# don't try to split strings without spaces
def with_unsplittable_string(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassNameWithoutAnySpacesWhatsoeverAndEvenMoreCharacters":
    pass

# output

# Long string example
def frobnicate() -> (
    "ThisIsTrulyUnreasonablyExtremelyLongClassName |"
    " list[ThisIsTrulyUnreasonablyExtremelyLongClassName]"
):
    pass


# split the string even when there are parameters
def frobnicate(a) -> (
    "ThisIsTrulyUnreasonablyExtremelyLongClassName |"
    " list[ThisIsTrulyUnreasonablyExtremelyLongClassName]"
):
    pass


# don't split strings followed by pragmas
def with_type_ignore(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # type: ignore
    pass


def with_fmt_skip(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # fmt: skip
    pass


# don't try to split strings without spaces
def with_unsplittable_string(
    a,
) -> "ThisIsTrulyUnreasonablyExtremelyLongClassNameWithoutAnySpacesWhatsoeverAndEvenMoreCharacters":
    pass
