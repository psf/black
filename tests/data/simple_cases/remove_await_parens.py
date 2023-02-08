import asyncio

# Control example
async def main():
    await asyncio.sleep(1)

# Remove brackets for short coroutine/task
async def main():
    await (asyncio.sleep(1))

async def main():
    await (
        asyncio.sleep(1)
    )

async def main():
    await (asyncio.sleep(1)
    )

# Check comments
async def main():
    await (  # Hello
        asyncio.sleep(1)
    )

async def main():
    await (
        asyncio.sleep(1)  # Hello
    )

async def main():
    await (
        asyncio.sleep(1)
    )  # Hello

# Long lines
async def main():
    await asyncio.gather(asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1))

# Same as above but with magic trailing comma in function
async def main():
    await asyncio.gather(asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1),)

# Cr@zY Br@ck3Tz
async def main():
    await (
        (((((((((((((
        (((        (((
        (((         (((
        (((         (((
        (((        (((
        ((black(1)))
        )))        )))
        )))         )))
        )))         )))
        )))        )))
        )))))))))))))
    )

# Keep brackets around non power operations and nested awaits
async def main():
    await (set_of_tasks | other_set)

async def main():
    await (await asyncio.sleep(1))

# It's awaits all the way down...
async def main():
    await (await x)

async def main():
    await (yield x)

async def main():
    await (await (asyncio.sleep(1)))

async def main():
    await (await (await (await (await (asyncio.sleep(1))))))

async def main():
    await (yield)

# output
import asyncio


# Control example
async def main():
    await asyncio.sleep(1)


# Remove brackets for short coroutine/task
async def main():
    await asyncio.sleep(1)


async def main():
    await asyncio.sleep(1)


async def main():
    await asyncio.sleep(1)


# Check comments
async def main():
    await asyncio.sleep(1)  # Hello


async def main():
    await asyncio.sleep(1)  # Hello


async def main():
    await asyncio.sleep(1)  # Hello


# Long lines
async def main():
    await asyncio.gather(
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
    )


# Same as above but with magic trailing comma in function
async def main():
    await asyncio.gather(
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
    )


# Cr@zY Br@ck3Tz
async def main():
    await black(1)


# Keep brackets around non power operations and nested awaits
async def main():
    await (set_of_tasks | other_set)


async def main():
    await (await asyncio.sleep(1))


# It's awaits all the way down...
async def main():
    await (await x)


async def main():
    await (yield x)


async def main():
    await (await asyncio.sleep(1))


async def main():
    await (await (await (await (await asyncio.sleep(1)))))


async def main():
    await (yield)
