# flags: --minimum-version=3.9
with ((a := 1)):
    pass
with (((a := 1))):
    pass
with ((a := (yield))):
    pass
with ((a := 1)), b:
    pass
async def f():
    async with ((a := 1)):
        pass
# output
with (a := 1):
    pass
with (a := 1):
    pass
with (a := (yield)):
    pass
with (a := 1), b:
    pass


async def f():
    async with (a := 1):
        pass
