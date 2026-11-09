help(lambda x=(
    # comment
    "bar",
): False)

result = (lambda x=(
    # a standalone comment
    1,
    2,
    3,
): x)

result = (  # comment
    lambda x=(
        # a standalone comment
        1,
    ): x
)

result = (  # comment
    lambda x=[
        # a standalone comment
        1,
    ]: x
).__name__


def f():
    return (  # comment
        lambda x=g(
            # a standalone comment
            1,
        ): x
    )

# output

help(
    lambda x=(
    # comment
    "bar",
    ): False
)

result = lambda x=(
    # a standalone comment
    1,
    2,
    3,
): x

result = (  # comment
    lambda x=(
    # a standalone comment
    1,
    ): x
)

result = (  # comment
    lambda x=[
    # a standalone comment
    1,
    ]: x
).__name__


def f():
    return (  # comment
        lambda x=g(
        # a standalone comment
        1,
        ): x
    )
