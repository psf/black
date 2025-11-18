# Test case for issue #4640
# Transformation test for standalone comments within parentheses in lambda default arguments

# Unformatted input with various cases of standalone comments in lambda default arguments
help(
    lambda x=(
    # comment at beginning
    "bar",
    ): False,
)

help(
    lambda x=("bar",
    # comment in middle
    ): False
)

help(
    lambda x=("extremely lengthy argument 1 extremely lengthy argument 1",
    # comment with long arguments
    "extremely lengthy argument 2 extremely lengthy argument 2",
    ): False,
)

help(
    lambda x=(
    # comment 1
    "bar",
    # comment 2
    "baz",
    # comment 3
    ): False
)

f = lambda x=(
    # comment 1
    "foo",
    # comment 2
    "bar",
    # comment 3
    "baz",
    # comment 4
): x

# output

# Test case for issue #4640
# Transformation test for standalone comments within parentheses in lambda default arguments

# Unformatted input with various cases of standalone comments in lambda default arguments
help(
    lambda x=(
    # comment at beginning
    "bar",
    ): False,
)

help(
    lambda x=("bar",
    # comment in middle
    ): False
)

help(
    lambda x=("extremely lengthy argument 1 extremely lengthy argument 1",
    # comment with long arguments
    "extremely lengthy argument 2 extremely lengthy argument 2",
    ): False,
)

help(
    lambda x=(
    # comment 1
    "bar",
    # comment 2
    "baz",
    # comment 3
    ): False
)

f = lambda x=(
    # comment 1
    "foo",
    # comment 2
    "bar",
    # comment 3
    "baz",
    # comment 4
): x
