l = [
    1,
    2
    # fmt: off
        # no touchy
    # fmt: on
]

l = [
    1,
    2,
    # fmt: off
        # no touchy
    # fmt: on
    3,
]

# fmt: on

    # I SHOULD be touched

# fmt: on


def this_SHOULD_be_touched():
# fmt: off
        # my indentation SHOULD be touched
    # fmt: on
    pass


def this_should_not_be_touched():
    """avoid SyntaxError docstring"""
    # fmt: off

        # my indentation shouldn't touched

    # fmt: on


# fmt: off
#poorly formatted comment
a=1
#another poorly formatted comment
#multiple lines are impacted
# fmt: on
#comment to correct
b=2


def this_should_also_not_be_touched():
    # fmt: off
    #my lack of initial space should stay unchanged

        #my indentation shouldn't touched

    # fmt: on
    pass


# fmt: off

    # my indentation shouldn't touched too

# fmt: on
a = 1

# output

l = [
    1,
    2
    # fmt: off
        # no touchy
    # fmt: on
]

l = [
    1,
    2,
    # fmt: off
        # no touchy
    # fmt: on
    3,
]

# fmt: on

# I SHOULD be touched

# fmt: on


def this_SHOULD_be_touched():
    # fmt: off
    # my indentation SHOULD be touched
    # fmt: on
    pass


def this_should_not_be_touched():
    """avoid SyntaxError docstring"""
    # fmt: off

        # my indentation shouldn't touched

    # fmt: on


# fmt: off
#poorly formatted comment
a=1
#another poorly formatted comment
#multiple lines are impacted
# fmt: on
# comment to correct
b = 2


def this_should_also_not_be_touched():
    # fmt: off
    #my lack of initial space should stay unchanged

        #my indentation shouldn't touched

    # fmt: on
    pass


# fmt: off

    # my indentation shouldn't touched too

# fmt: on
a = 1
