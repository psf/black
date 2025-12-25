# flags: --preview

foo(
    # with extra parens
    bar=x if y else z,
    bar=x or y,
    bar=not x,
    bar=x < y < z,
    bar=x + y,
    bar=f(x) ** y,
    bar=await f(),
    # without extra parens
    bar=-x,
    bar=x**y,
    bar=x.y.z,
    bar=f(x, y),
    bar=(x, y),
    bar=[x + y],
    bar=f"{x + y}",
    bar=lambda: x + y,
)


@foo(bar=x ** y, bar=x + y)
def foo(bar=x ** y, bar=x + y, bar: int=x + y):
    return lambda bar=x ** y, bar=x + y: x + y


# output

foo(
    # with extra parens
    bar=(x if y else z),
    bar=(x or y),
    bar=(not x),
    bar=(x < y < z),
    bar=(x + y),
    bar=(f(x) ** y),
    bar=(await f()),
    # without extra parens
    bar=-x,
    bar=x**y,
    bar=x.y.z,
    bar=f(x, y),
    bar=(x, y),
    bar=[x + y],
    bar=f"{x + y}",
    bar=lambda: x + y,
)


@foo(bar=x**y, bar=(x + y))
def foo(bar=x**y, bar=(x + y), bar: int = x + y):
    return lambda bar=x**y, bar=(x + y): x + y
