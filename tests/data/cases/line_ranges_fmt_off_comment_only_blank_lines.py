# flags: --line-ranges=35-35
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The blank lines between a fmt: off/on block that holds only comments and the
# statement after it are kept when that statement is outside of the range.
x = 1
# fmt: off
#---------+
# fmt: on


TIMEOUT = 30


def f():
    # fmt: off
    #   keep   this
    # fmt: on

    return  1


# fmt: off
# a   b
# fmt: on

y = 2
# fmt: off
# c   d
# fmt: on


z = 3
retries  =  3

# output
# flags: --line-ranges=35-35
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The blank lines between a fmt: off/on block that holds only comments and the
# statement after it are kept when that statement is outside of the range.
x = 1
# fmt: off
#---------+
# fmt: on


TIMEOUT = 30


def f():
    # fmt: off
    #   keep   this
    # fmt: on

    return  1


# fmt: off
# a   b
# fmt: on

y = 2
# fmt: off
# c   d
# fmt: on


z = 3
retries = 3
