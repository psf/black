# flags: --preview
if TYPE_CHECKING:
    def pixmap(*args: Any, **kwargs: Any) -> Any: ...
else:
    def pixmap(*args: Any, **kwargs: Any) -> Any: ...


def outer():
    if first:

        @decorate
        async def run():
            return first

    elif second:
        async def run():
            return second
    else:
        initialize()

        async def run():
            return fallback

    return run


for item in items:

    def callback():
        return item

else:

    def callback():
        return default


if ready:

    initialize()


# output
if TYPE_CHECKING:
    def pixmap(*args: Any, **kwargs: Any) -> Any: ...
else:
    def pixmap(*args: Any, **kwargs: Any) -> Any: ...


def outer():
    if first:
        @decorate
        async def run():
            return first
    elif second:
        async def run():
            return second
    else:
        initialize()

        async def run():
            return fallback

    return run


for item in items:

    def callback():
        return item

else:

    def callback():
        return default


if ready:

    initialize()
