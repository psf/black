# Statements right after a fmt: off/on block that holds only comments.
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
    return 1


class Config:
    # fmt: off
    #   name     value
    # fmt: on
    debug = True
