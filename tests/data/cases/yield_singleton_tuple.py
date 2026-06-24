# flags: --preview

def f():
    yield x,


# output


def f():
    yield (x,)
