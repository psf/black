# flags: --preview
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = 5  # ruff: ignore[B018]
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = 5  # ruff:ignore[B018]

# A multiline expression must not collapse into one long line.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = (
    some_long_function_name(argument_one, argument_two, argument_three, argument_four)
)  # ruff: ignore[B018]

# An own-line ignore must not prevent formatting the next statement.
# ruff: ignore[B018]
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = 123456789012345678901234567890

# output
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = 5  # ruff: ignore[B018]
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = 5  # ruff:ignore[B018]

# A multiline expression must not collapse into one long line.
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = (
    some_long_function_name(argument_one, argument_two, argument_three, argument_four)
)  # ruff: ignore[B018]

# An own-line ignore must not prevent formatting the next statement.
# ruff: ignore[B018]
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = (
    123456789012345678901234567890
)
