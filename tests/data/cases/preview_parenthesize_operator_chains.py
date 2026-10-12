# flags: --preview

# Regression test for https://github.com/psf/black/issues/4455.
value = (
    some_long_function_call(first_arg, second_arg)
    + some_other_function_call(third_arg, fourth_arg)
)
unparenthesized = some_long_function_call(first_arg, second_arg) + some_other_function_call(third_arg, fourth_arg)

# Arithmetic, bitwise, and comparison operators get the same treatment.
subtraction = some_long_function_call(first_arg, second_arg) - some_other_function_call(third_arg, fourth_arg)
multiplication = some_long_function_call(first_arg, second_arg) * some_other_function_call(third_arg, fourth_arg)
division = some_long_function_call(first_arg, second_arg) / some_other_function_call(third_arg, fourth_arg)
bitwise_or = some_long_function_call(first_arg, second_arg) | some_other_function_call(third_arg, fourth_arg)
equality = some_long_function_call(first_arg, second_arg) == some_other_function_call(third_arg, fourth_arg)
inequality = some_long_function_call(first_arg, second_arg) != some_other_function_call(third_arg, fourth_arg)
greater_equal = some_long_function_call(first_arg, second_arg) >= some_other_function_call(third_arg, fourth_arg)

# Control flow expressions: return, yield, if.
def example_return():
    return some_long_function_call(first_arg, second_arg) + some_other_function_call(third_arg, fourth_arg)

def example_yield():
    yield some_long_function_call(first_arg, second_arg) + some_other_function_call(third_arg, fourth_arg)

if some_long_function_call(first_arg, second_arg) == some_other_function_call(third_arg, fourth_arg):
    pass

# Comments attached to an operand are preserved.
commented = (
    some_long_function_call(first_arg, second_arg)  # first call
    + some_other_function_call(third_arg, fourth_arg)
)

# Chained operations with multiple operators already use normal delimiter split.
chained = some_func_a(first_arg, second_arg) + some_func_b(third_arg, fourth_arg) + some_func_c(fifth_arg, sixth_arg)

# Short expressions that fit on a single line remain untouched.
short_sum = func_a(x) + func_b(y)

# Operands that individually exceed line length retain previous unparenthesized split.
overlong_right = some_call(arg1, arg2) + some_extremely_long_function_call_that_exceeds_eighty_eight_characters_by_itself(arg3, arg4)
overlong_left = (
    some_extremely_long_function_call_that_exceeds_eighty_eight_characters_by_itself(
        arg1, arg2
    )
    + some_call(arg3, arg4)
)

# Operands with magic trailing commas retain multiline argument splitting.
magic_left = func(
    first_arg,
    second_arg,
) + other(third_arg, fourth_arg)
magic_right = other(third_arg, fourth_arg) + func(
    first_arg,
    second_arg,
)

# output

# Regression test for https://github.com/psf/black/issues/4455.
value = (
    some_long_function_call(first_arg, second_arg)
    + some_other_function_call(third_arg, fourth_arg)
)
unparenthesized = (
    some_long_function_call(first_arg, second_arg)
    + some_other_function_call(third_arg, fourth_arg)
)

# Arithmetic, bitwise, and comparison operators get the same treatment.
subtraction = (
    some_long_function_call(first_arg, second_arg)
    - some_other_function_call(third_arg, fourth_arg)
)
multiplication = (
    some_long_function_call(first_arg, second_arg)
    * some_other_function_call(third_arg, fourth_arg)
)
division = (
    some_long_function_call(first_arg, second_arg)
    / some_other_function_call(third_arg, fourth_arg)
)
bitwise_or = (
    some_long_function_call(first_arg, second_arg)
    | some_other_function_call(third_arg, fourth_arg)
)
equality = (
    some_long_function_call(first_arg, second_arg)
    == some_other_function_call(third_arg, fourth_arg)
)
inequality = (
    some_long_function_call(first_arg, second_arg)
    != some_other_function_call(third_arg, fourth_arg)
)
greater_equal = (
    some_long_function_call(first_arg, second_arg)
    >= some_other_function_call(third_arg, fourth_arg)
)


# Control flow expressions: return, yield, if.
def example_return():
    return (
        some_long_function_call(first_arg, second_arg)
        + some_other_function_call(third_arg, fourth_arg)
    )


def example_yield():
    yield (
        some_long_function_call(first_arg, second_arg)
        + some_other_function_call(third_arg, fourth_arg)
    )


if (
    some_long_function_call(first_arg, second_arg)
    == some_other_function_call(third_arg, fourth_arg)
):
    pass

# Comments attached to an operand are preserved.
commented = (
    some_long_function_call(first_arg, second_arg)  # first call
    + some_other_function_call(third_arg, fourth_arg)
)

# Chained operations with multiple operators already use normal delimiter split.
chained = (
    some_func_a(first_arg, second_arg)
    + some_func_b(third_arg, fourth_arg)
    + some_func_c(fifth_arg, sixth_arg)
)

# Short expressions that fit on a single line remain untouched.
short_sum = func_a(x) + func_b(y)

# Operands that individually exceed line length retain previous unparenthesized split.
overlong_right = some_call(
    arg1, arg2
) + some_extremely_long_function_call_that_exceeds_eighty_eight_characters_by_itself(
    arg3, arg4
)
overlong_left = (
    some_extremely_long_function_call_that_exceeds_eighty_eight_characters_by_itself(
        arg1, arg2
    )
    + some_call(arg3, arg4)
)

# Operands with magic trailing commas retain multiline argument splitting.
magic_left = func(
    first_arg,
    second_arg,
) + other(third_arg, fourth_arg)
magic_right = other(third_arg, fourth_arg) + func(
    first_arg,
    second_arg,
)
