# `# fmt: off` after the last item in brackets, before its trailing comma or the rest
# of the item. No trailing comma should be added before the region.

x = [a,  b
    # fmt: off
    ,
]

foo(a,
    b  # comment
    # fmt: off
    ,  c
)

foo(
    a,
    b
    # fmt: off
    ,
    # fmt: on
)

from a import (
    b
    # fmt: off
    ,
)

def f(
    a
    # fmt: off
    ,
):
    pass

def f(
    a,
    b
    # fmt: off
    = 1
):
    pass

x = [a,  b
    # fmt: off
    + 1
]

foo(a,  b
    # fmt: off
    .c(  d )
)

# output

# `# fmt: off` after the last item in brackets, before its trailing comma or the rest
# of the item. No trailing comma should be added before the region.

x = [
    a,
    b
    # fmt: off
    ,
]

foo(
    a,
    b  # comment
    # fmt: off
    ,  c
)

foo(
    a,
    b
    # fmt: off
    ,
    # fmt: on
)

from a import (
    b
    # fmt: off
    ,
)


def f(
    a
    # fmt: off
    ,
):
    pass


def f(
    a,
    b
    # fmt: off
    = 1
):
    pass


x = [
    a,
    b
    # fmt: off
    + 1
]

foo(
    a,
    b
    # fmt: off
    .c(  d )
)
