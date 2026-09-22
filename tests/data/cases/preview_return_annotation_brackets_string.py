# flags: --unstable
# Long string example
def frobnicate() -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# split the string even when there are parameters
def frobnicate(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
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
