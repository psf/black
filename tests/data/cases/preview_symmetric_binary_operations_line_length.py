# flags: --preview --line-length=60

# Split before the operator when the operation doesn't fit inside the parentheses.
value = first_function_name(argument) + second_function(other_arg)

# Stay on one line inside the parentheses when it fits.
total_value = first_function(argument) + second_function(arg)

# Keep the existing formatting when an operand doesn't fit on its own line.
long_operand = first_function_with_name(first_argument, second_argument_x) + f(x)

# Short operations stay on one line.
short = first_function(argument) + second_function(arg)

# output

# Split before the operator when the operation doesn't fit inside the parentheses.
value = (
    first_function_name(argument)
    + second_function(other_arg)
)

# Stay on one line inside the parentheses when it fits.
total_value = (
    first_function(argument) + second_function(arg)
)

# Keep the existing formatting when an operand doesn't fit on its own line.
long_operand = first_function_with_name(
    first_argument, second_argument_x
) + f(x)

# Short operations stay on one line.
short = first_function(argument) + second_function(arg)
