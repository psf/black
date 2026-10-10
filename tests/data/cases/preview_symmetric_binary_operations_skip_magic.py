# flags: --preview --skip-magic-trailing-comma

# Ignored trailing commas do not prevent symmetric formatting.
value = first_function_with_long_name(argument,) + second_function_with_long_name(argument)

# output

# Ignored trailing commas do not prevent symmetric formatting.
value = (
    first_function_with_long_name(argument)
    + second_function_with_long_name(argument)
)
