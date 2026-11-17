# flags: --line-ranges=4-4 --line-ranges=18-18
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
x  =  1


@dec
async def fetch(x):  # fmt: skip
    return x + 1


async with ctx() as c:  # fmt: skip
    pass


async for item in items:  # fmt: skip
    pass
y  =  2

# output

# flags: --line-ranges=4-4 --line-ranges=18-18
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.
x = 1


@dec
async def fetch(x):  # fmt: skip
    return x + 1


async with ctx() as c:  # fmt: skip
    pass


async for item in items:  # fmt: skip
    pass
y = 2
