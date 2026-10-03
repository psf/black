# The parentheses here belong to the tuple that is used as the context
# expression, not to the `with` statement. Dropping them turns a single context
# manager into several, which is a different program (and here, a TypeError at
# runtime).
with ((a, b)):
    pass

with ((a, b), c):
    pass

with (c, (a, b)):
    pass

with ((a, b), (c, d)):
    pass

with (((a, b))):
    pass

with (a, b):
    pass


async def f():
    async with ((a, b)):
        pass

# output

# The parentheses here belong to the tuple that is used as the context
# expression, not to the `with` statement. Dropping them turns a single context
# manager into several, which is a different program (and here, a TypeError at
# runtime).
with ((a, b)):
    pass

with (a, b), c:
    pass

with c, (a, b):
    pass

with (a, b), (c, d):
    pass

with (((a, b))):
    pass

with a, b:
    pass


async def f():
    async with ((a, b)):
        pass
