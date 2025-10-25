async def func() -> (int):
    return 0


@decorated
async def func() -> (int):
    return 0


async for (item) in async_iter:
    pass


async def greet_person(name: str = "world") -> None:
    print(f"Hello {name}")


async for (a, b) in async_iter:
    print(a, b)

# output


async def func() -> int:
    return 0


@decorated
async def func() -> int:
    return 0


async for item in async_iter:
    pass


async def greet_person(name: str = "world") -> None:
    print(f"Hello {name}")


async for a, b in async_iter:
    print(a, b)