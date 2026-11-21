# flags: --preview
x = [
    a
    for a in (  # comment
        lambda: 1
    )
]
x = [
    a
    for a in (
        b if c else d  # comment
    )
]
x = [
    a
    for a in (
        b := c  # comment
    )
]
[a for a in (b := c)]
{a for a in (b := c)}
{a: a for a in (b := c)}
(a for a in (b := c))
print(a for a in (b := c))
[a for a in ((b := c))]


def f():
    return [a for a in (yield)]


def g():
    return [a for a in ((yield))]


def h():
    return [a for a in (x := (yield))]


async def i():
    return [a async for a in (b := c)]
# output
x = [a for a in (lambda: 1)]  # comment
x = [a for a in (b if c else d)]  # comment
x = [a for a in (b := c)]  # comment
[a for a in (b := c)]
{a for a in (b := c)}
{a: a for a in (b := c)}
(a for a in (b := c))
print(a for a in (b := c))
[a for a in (b := c)]


def f():
    return [a for a in (yield)]


def g():
    return [a for a in (yield)]


def h():
    return [a for a in (x := (yield))]


async def i():
    return [a async for a in (b := c)]
