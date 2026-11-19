# flags: --preview --skip-magic-trailing-comma

# Ignored trailing commas do not prevent parenthesized operator chain formatting.
magic_left = some_long_function_call(
    first_arg,
    second_arg,
) + some_other_function_call(third_arg, fourth_arg)
magic_right = some_other_function_call(third_arg, fourth_arg) + some_long_function_call(
    first_arg,
    second_arg,
)

# output

# Ignored trailing commas do not prevent parenthesized operator chain formatting.
magic_left = (
    some_long_function_call(first_arg, second_arg)
    + some_other_function_call(third_arg, fourth_arg)
)
magic_right = (
    some_other_function_call(third_arg, fourth_arg)
    + some_long_function_call(first_arg, second_arg)
)
