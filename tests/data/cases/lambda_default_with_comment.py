# Test case for issue #4640
# Standalone comment within parentheses in lambda default arguments

# Basic case: Comment at the beginning of lambda default arguments
help(
    lambda x=(
    # comment
    "bar",
    ): False,
)

# Basic case: Comment in the middle of lambda default arguments
help(
    lambda x=("bar",
    # comment
    ): False
)

# Basic case: Comment with long arguments
help(
    lambda x=("extremely lengthy argument 1 extremely lengthy argument 1",
    # comment
    "extremely lengthy argument 2 extremely lengthy argument 2",
    ): False,
)

# Edge case: Multiple comments in different positions
help(
    lambda x=(
    # comment 1
    "bar",
    # comment 2
    "baz",
    # comment 3
    ): False,
)

# Edge case: Nested lambdas with comments
help(
    lambda x=(
    # comment before nested lambda
    lambda y: (
        # comment inside nested lambda
        y
        + 1
    ),
    ): False,
)

# Edge case: Comments with special characters
help(
    lambda x=(
    # comment with * and ** and () and [] and {}
    "bar",
    ): False,
)

# Edge case: Empty tuple with comment
help(
    lambda x=(
    # comment in empty tuple
    ): False,
)

# Edge case: Comment at the beginning and end
help(
    lambda x=(
    # comment at beginning
    "bar", "baz",
    # comment at end
    ): False,
)

# Edge case: Multiple arguments with multiple comments
f = lambda x=(
    # comment 1
    "foo",
    # comment 2
    "bar",
    # comment 3
    "baz",
    # comment 4
): x
