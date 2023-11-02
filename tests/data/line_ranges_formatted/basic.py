"""Module doc."""

from typing import (
    Callable,
    Literal,
)


# fmt: off
class  Unformatted:
  def   should_also_work(self):
    pass
# fmt: on


a   = [1, 2]  # fmt: skip


# This should cover as many syntaxes as possible.
class Foo:
    """Class doc."""

    def __init__(self) -> None:
        pass

    @add_logging
    @memoize.memoize(max_items=2)
    def plus_one(
        self,
        number: int,
    ) -> int:
        return number + 1

    async def async_plus_one(self, number: int) -> int:
        await asyncio.sleep(1)
        async with some_context():
            return number + 1


try:
    for i in range(10):
        while condition:
            if something:
                then_something()
            elif something_else:
                then_something_else()
except ValueError as e:
    handle(e)
finally:
    done()
