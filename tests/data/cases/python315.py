# flags: --fast
lazy import json
lazy from package.subpackage import (
    alpha,
    beta,
    gamma,
)
from .lazy import thing

lazy = "still an identifier"


def eager():
    lazy = "still an identifier"
    return lazy


flattened = [*item for item in items]
generator = (*item for item in items)
combined = {*members for members in groups}
merged = {**mapping for mapping in mappings}


async def collect():
    return [*item async for item in items_async]


# output
lazy import json
lazy from package.subpackage import (
    alpha,
    beta,
    gamma,
)
from .lazy import thing

lazy = "still an identifier"


def eager():
    lazy = "still an identifier"
    return lazy


flattened = [*item for item in items]
generator = (*item for item in items)
combined = {*members for members in groups}
merged = {**mapping for mapping in mappings}


async def collect():
    return [*item async for item in items_async]
