# Regression for https://github.com/psf/black/issues/3741
# An inline comment after the closing bracket of optional parentheses must stay
# there when the parentheses contain own-line comments and so cannot be removed.
x = 1
# Leading comment
del (
    # First inner own-line
    x  # Trailing comment same-line
    # Trailing comment own-line last inner
)  # Trailing same-block
# Trailing own-line

del (
    # first
    x
)  # trailing

value = (
    x
    # last
)  # trailing


def f():
    return (
        x
        # last
    )  # trailing


assert (
    x
    # last
)  # trailing

assert foo(
    # inside the call
    1
), (message)  # trailing

for item in (
    items
    # last
):  # trailing
    pass

# Without own-line comments the parentheses go away and the comment moves along.
del (
    x
)  # trailing

# output

# Regression for https://github.com/psf/black/issues/3741
# An inline comment after the closing bracket of optional parentheses must stay
# there when the parentheses contain own-line comments and so cannot be removed.
x = 1
# Leading comment
del (
    # First inner own-line
    x  # Trailing comment same-line
    # Trailing comment own-line last inner
)  # Trailing same-block
# Trailing own-line

del (
    # first
    x
)  # trailing

value = (
    x
    # last
)  # trailing


def f():
    return (
        x
        # last
    )  # trailing


assert (
    x
    # last
)  # trailing

assert foo(
    # inside the call
    1
), message  # trailing

for item in (
    items
    # last
):  # trailing
    pass

# Without own-line comments the parentheses go away and the comment moves along.
del x  # trailing
