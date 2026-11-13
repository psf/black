# flags: --preview
x = [
    # fmt: off
    1
]

x: Final[
    # fmt: off
    str
] = "a"

x = f(
    # fmt: off
    'a'
      # comment
)

assert (
    # fmt: off
    a
), "message"

from a import (
    # fmt: off
    b
)

x = [
    # fmt: off
    1
]
# fmt: on
y  =  2


def f():
    if x:
        return [
            # fmt: off
            1
        ]
    return  None

# output
x = [
    # fmt: off
    1
]

x: Final[
    # fmt: off
    str
] = "a"

x = f(
    # fmt: off
    'a'
      # comment
)

assert (
    # fmt: off
    a
), "message"

from a import (
    # fmt: off
    b
)

x = [
    # fmt: off
    1
]
# fmt: on
y = 2


def f():
    if x:
        return [
            # fmt: off
            1
        ]
    return None
