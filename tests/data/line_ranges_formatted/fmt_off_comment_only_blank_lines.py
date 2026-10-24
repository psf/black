# Blank lines right after a fmt: off/on block that holds only comments.
x = 1
# fmt: off
#---------+
# fmt: on


TIMEOUT = 30


def f():
    # fmt: off
    #   keep   this
    # fmt: on

    return 1


# fmt: off
# a   b
# fmt: on

y = 2
