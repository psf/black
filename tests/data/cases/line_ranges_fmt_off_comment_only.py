# flags: --line-ranges=29-29
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The statements outside of the range come right after a fmt: off/on block that
# holds only comments. They stay on their own line instead of being appended to the
# closing fmt: on comment, which would turn them into part of the comment.
# fmt: off
#---------+---------#
#  name   |  value  #
#---------+---------#
# fmt: on
TIMEOUT = 30


def f():
    # fmt: off
    #   keep   this
    # fmt: on
    return  1


class Config:
    # fmt: off
    #   name     value
    # fmt: on
    debug  =  True

retries  =  3

# output
# flags: --line-ranges=29-29
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The statements outside of the range come right after a fmt: off/on block that
# holds only comments. They stay on their own line instead of being appended to the
# closing fmt: on comment, which would turn them into part of the comment.
# fmt: off
#---------+---------#
#  name   |  value  #
#---------+---------#
# fmt: on
TIMEOUT = 30


def f():
    # fmt: off
    #   keep   this
    # fmt: on
    return  1


class Config:
    # fmt: off
    #   name     value
    # fmt: on
    debug  =  True

retries = 3
