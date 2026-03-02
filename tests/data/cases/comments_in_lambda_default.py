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

# output

help(
    lambda x=(
    # comment
    "bar",
    ): False,
)

result = lambda x=(
    # a standalone comment
    1,
    2,
    3,
): x
