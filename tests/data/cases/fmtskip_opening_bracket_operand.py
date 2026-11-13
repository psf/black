# `# fmt: skip` on an opening bracket that starts an operand of a longer expression
# hides the whole line, including the code before the bracket.

with (  # fmt: skip
    a
) == 1 and b:
    x  =  1

with not (  # fmt: skip
    a
) or b as c:
    pass

with -(  # fmt: skip
    a
).real and b:
    pass

x = (  # fmt: skip
    a
) + 1 or b

y = not [  # fmt: skip
    1, 2] and c

assert (  # fmt: skip
    a
) * 2 + 1 == b


async def f():
    async with (  # fmt: skip
        a
    ) in b and c:
        pass


def g():
    yield (  # fmt: skip
        a
    ) == 1 and b
    yield not (  # fmt: skip
        a
    ) or b
    return -{  # fmt: skip
        "a": 1}.keys or b

# output

# `# fmt: skip` on an opening bracket that starts an operand of a longer expression
# hides the whole line, including the code before the bracket.

with (  # fmt: skip
    a
) == 1 and b:
    x = 1

with not (  # fmt: skip
    a
) or b as c:
    pass

with -(  # fmt: skip
    a
).real and b:
    pass

x = (  # fmt: skip
    a
) + 1 or b

y = not [  # fmt: skip
    1, 2] and c

assert (  # fmt: skip
    a
) * 2 + 1 == b


async def f():
    async with (  # fmt: skip
        a
    ) in b and c:
        pass


def g():
    yield (  # fmt: skip
        a
    ) == 1 and b
    yield not (  # fmt: skip
        a
    ) or b
    return -{  # fmt: skip
        "a": 1}.keys or b
