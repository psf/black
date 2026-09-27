# flags: --preview
# Issue 3113: Expressions with parameter comments should be parenthesized when exceeding line length

long_variable_name_for_testing_purposes_only = some_long_function_name_for_testing_purposes(
    first_argument,
    # comment between parameters
    second_argument,
)

# Multiple parameter comments
another_long_variable_name_for_testing_purposes = another_long_function_name_for_testing_calls(
    # comment before first parameter
    first_argument,
    # comment between parameters
    second_argument,
    # comment after last parameter
    third_argument,
)

# Fits on line without parenthesizing: should not wrap
short_variable = short_function_name(
    first_arg,
    # comment
    second_arg,
)

class MyClass:
    def my_method(self):
        long_variable_name_for_testing_method = some_long_function_name_for_testing_calls(
            first_argument,
            # comment
            second_argument,
        )

# output

# Issue 3113: Expressions with parameter comments should be parenthesized when exceeding line length

long_variable_name_for_testing_purposes_only = (
    some_long_function_name_for_testing_purposes(
        first_argument,
        # comment between parameters
        second_argument,
    )
)

# Multiple parameter comments
another_long_variable_name_for_testing_purposes = (
    another_long_function_name_for_testing_calls(
        # comment before first parameter
        first_argument,
        # comment between parameters
        second_argument,
        # comment after last parameter
        third_argument,
    )
)

# Fits on line without parenthesizing: should not wrap
short_variable = short_function_name(
    first_arg,
    # comment
    second_arg,
)


class MyClass:
    def my_method(self):
        long_variable_name_for_testing_method = (
            some_long_function_name_for_testing_calls(
                first_argument,
                # comment
                second_argument,
            )
        )
