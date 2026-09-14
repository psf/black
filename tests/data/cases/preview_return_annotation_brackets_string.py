# flags: --unstable
# Long string example
def frobnicate() -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# splitting the string breaks if there's any parameters
def frobnicate(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# Strings without a legal split point remain unwrapped.
def frobnicate(a) -> "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
    pass

# Pragmas keep the annotation on its original logical line.
def frobnicate(a) -> ("ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]"  # noqa
):
    pass

# Type ignores also keep the annotation on its original logical line.
def frobnicate(a) -> ("ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]"):  # type: ignore
    pass

# Triple-quoted strings cannot be split by StringSplitter.
def frobnicate(a) -> """ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]""":
    pass

# output

# Long string example
def frobnicate() -> (
    "ThisIsTrulyUnreasonablyExtremelyLongClassName |"
    " list[ThisIsTrulyUnreasonablyExtremelyLongClassName]"
):
    pass


# splitting the string breaks if there's any parameters
def frobnicate(
    a,
) -> (
    "ThisIsTrulyUnreasonablyExtremelyLongClassName |"
    " list[ThisIsTrulyUnreasonablyExtremelyLongClassName]"
):
    pass


# Strings without a legal split point remain unwrapped.
def frobnicate(
    a,
) -> "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
    pass


# Pragmas keep the annotation on its original logical line.
def frobnicate(
    a,
) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # noqa
    pass


# Type ignores also keep the annotation on its original logical line.
def frobnicate(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # type: ignore
    pass


# Triple-quoted strings cannot be split by StringSplitter.
def frobnicate(
    a,
) -> """ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]""":
    pass
