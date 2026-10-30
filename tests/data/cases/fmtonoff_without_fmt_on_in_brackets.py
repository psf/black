# A `# fmt: off` without `# fmt: on` inside brackets lasts until the closing bracket,
# also when the brackets hold a single name, number or string.

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

print(
    # fmt: off
    a
)


class A(
    # fmt: off
    B
):
    x  =  1


def f():
    if x:
        return [
            # fmt: off
            1
        ]
    return  None

# output

# A `# fmt: off` without `# fmt: on` inside brackets lasts until the closing bracket,
# also when the brackets hold a single name, number or string.

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

print(
    # fmt: off
    a
)


class A(
    # fmt: off
    B
):
    x = 1


def f():
    if x:
        return [
            # fmt: off
            1
        ]
    return None
