# A `# fmt: skip` on the header of a function or class whose body is only `...`
# used to crash for `async def` (the `...` lost its indentation) and to indent
# the `...` by one space for `def` and `class`.
async def fetch( ):  # fmt: skip
    ...


def compute( ):  # fmt: skip
    ...


class Proto( object ):  # fmt: skip
    ...


class Service:
    async def handle( self ):  # fmt: skip
        ...

    def close( self ):  # fmt: skip
        ...
