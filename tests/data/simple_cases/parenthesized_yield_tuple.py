async def main():
    yield x
    (yield x)
    await (yield x)


# Regression test for https://github.com/psf/black/issues/3851.
def f():
    yield x,
    return x,

    yield (y,)
    yield from (y,)
    return (y,)

    yield this_variable_is_over_the_line_length_limit_of_88_______________________________________,
    return this_variable_is_over_the_line_length_limit_of_88_______________________________________,

    yield (this_variable_is_over_the_line_length_limit_of_88_______________________________________,)
    yield from (this_variable_is_over_the_line_length_limit_of_88_______________________________________,)
    return (this_variable_is_over_the_line_length_limit_of_88_______________________________________,)

    yield """
        multiline string
    """,
    return """
        multiline string
    """,

    yield ("""
        multiline string
    """,)
    yield from ("""
        multiline string
    """,)
    return ("""
        multiline string
    """,)


# output


async def main():
    yield x
    (yield x)
    await (yield x)


# Regression test for https://github.com/psf/black/issues/3851.
def f():
    yield (x,)
    return (x,)

    yield (y,)
    yield from (y,)
    return (y,)

    yield (
        this_variable_is_over_the_line_length_limit_of_88_______________________________________,
    )
    return (
        this_variable_is_over_the_line_length_limit_of_88_______________________________________,
    )

    yield (
        this_variable_is_over_the_line_length_limit_of_88_______________________________________,
    )
    yield from (
        this_variable_is_over_the_line_length_limit_of_88_______________________________________,
    )
    return (
        this_variable_is_over_the_line_length_limit_of_88_______________________________________,
    )

    yield (
        """
        multiline string
    """,
    )
    return (
        """
        multiline string
    """,
    )

    yield (
        """
        multiline string
    """,
    )
    yield from (
        """
        multiline string
    """,
    )
    return (
        """
        multiline string
    """,
    )
