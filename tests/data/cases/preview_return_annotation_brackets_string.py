# flags: --preview
# Long string example
def frobnicate() -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# splitting the string breaks if there's any parameters
def frobnicate(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
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
) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass
