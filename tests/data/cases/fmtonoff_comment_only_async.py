# A comment-only `# fmt: off` / `# fmt: on` block right before an async statement
# used to make Black drop the statement (an error, or lost code with --fast).
x = 1
# fmt: off
# fmt: on
async def f( ):
    pass
# fmt: off
#   keep  this
# fmt: on
async def g( ):  # fmt: skip
    pass
async def h():
    # fmt: off
    # fmt: on
    async with a  as b:
        pass
    # fmt: off
    # fmt: on
    async for i in  c:
        pass

# output

# A comment-only `# fmt: off` / `# fmt: on` block right before an async statement
# used to make Black drop the statement (an error, or lost code with --fast).
x = 1


# fmt: off
# fmt: on
async def f():
    pass


# fmt: off
#   keep  this
# fmt: on
async def g( ):  # fmt: skip
    pass


async def h():
    # fmt: off
    # fmt: on
    async with a as b:
        pass
    # fmt: off
    # fmt: on
    async for i in c:
        pass
