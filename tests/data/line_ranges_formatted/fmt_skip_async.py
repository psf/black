# Top-level async statements with `# fmt: skip` headers stay intact when
# any individual line is selected via `--line-ranges`.
x = 1


@dec
async def fetch(x):  # fmt: skip
    return x + 1


async def stub():  # fmt: skip
    ...


async with ctx() as c:  # fmt: skip
    pass


async for item in items:  # fmt: skip
    pass


y = 2
