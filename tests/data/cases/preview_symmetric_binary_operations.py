# flags: --preview

# Regression tests for https://github.com/psf/black/issues/4455.
value = get_value_from_a_kinda_long_function_that_is_even_longer()  + max(offset, threshold)


class SomeClass:
    def some_method(value):
        return self.another_method(value - max_size) + self.another_method(min_size - value)


# Chains of three or more operands already split before every operator.
value = get_value_from_a_kinda_long_function() + previous_values[-1] + max(offset, threshold)


# Tuples are not binary operations.
def prepare_batch(batch, device, non_blocking):
    x, y = batch["image"].to(device, non_blocking=non_blocking), batch["label"].to(device, non_blocking=non_blocking)


# Every arithmetic and bitwise binary operator is split the same way.
difference = first_function_with_long_name(argument) - second_function_with_long_name(arg)
product = first_function_with_long_name(argument) * second_function_with_long_name(argument)
quotient = first_function_with_long_name(argument) / second_function_with_long_name(argument)
floor_quotient = first_function_with_long_name(argument) // second_function_with_long_name(arg)
remainder = first_function_with_long_name(argument) % second_function_with_long_name(argument)
matrix_product = first_function_with_long_name(argument) @ second_function_with_long_name(arg)
power = first_function_with_long_name(argument) ** second_function_with_long_name(argument)
left_shift = first_function_with_long_name(argument) << second_function_with_long_name(arg)
right_shift = first_function_with_long_name(argument) >> second_function_with_long_name(arg)
bitwise_and = first_function_with_long_name(argument) & second_function_with_long_name(arg)
bitwise_xor = first_function_with_long_name(argument) ^ second_function_with_long_name(arg)
bitwise_or = first_function_with_long_name(argument) | second_function_with_long_name(arg)

# This includes string formatting with a tuple of arguments.
message = "Something went wrong with %s while processing the request %s" % (first, second)

# Operands may contain attribute access, subscripts, unary operators, and operators
# with a higher priority.
total = self.first_attribute.compute(first_argument) + self.second_attribute[some_key](arg)
total = -first_function_with_long_name(argument) + second_function_with_long_name(argument)
total = first_value * first_function_with_long_name(argument) + second_function_name(arg)


async def main():
    result = await first_function_with_long_name(argument) + second_function_name(argument)


# Other statements with optional parentheses are split the same way.
def f():
    if first_function_with_long_name(argument) + second_function_with_long_name(argument):
        return first_function_with_long_name(argument) + second_function_with_long_name(arg)
    for item in first_function_with_long_name(argument) + second_function_with_long_name(arg):
        pass


some_dict["with_a_long_key"] = some_function_name(first_argument) + other_function(second)
some_object.some_attribute_with_a_very_long_name["some_key_with_a_long_name"] = first(arg) + second(arg)

# Comments on an operand stay attached and formatting remains stable.
commented_left = (
    first_function_with_long_name(argument)  # first
    + second_function_with_long_name(argument)
)
commented_right = (
    first_function_with_long_name(argument)
    + second_function_with_long_name(argument)  # second
)
comment_in_operand = first_function_with_long_name(  # comment
    argument
) + second_function_with_long_name(argument)

# Operands that would still be split keep the existing formatting.
long_left = first_function_with_a_really_long_name(first_argument, second_argument, third_argument_value) + f(x)
long_right = f(x) + first_function_with_a_really_long_name(first_argument, second_argument, third_argument_value)
magic_trailing_comma = first_function(argument,) + second_function_with_a_long_name(argument_value)
multiline_string = """
text
""" + second_function_with_a_long_name(argument_value, another_argument_value, third_one)

# Splitting before the operator would misrepresent precedence.
negation = not some_function_with_long_name(argument) + other_function_with_long_name(arg)
handler = lambda event: process_the_event_with_long_name(event) + finalize_event(event_id)

# Comparisons and boolean operations are unchanged.
assert some_function_with_a_long_name(argument_one) == other_function_long_name(argument)
condition = some_function_with_a_long_name(argument_one) and other_function_long_name(arg)

# Operations that already keep their optional parentheses are unchanged.
some_variable_name = some_long_function_name(argument_one) + another_long_variable_name_here
mapping = {
    "some_key": first_function_with_long_name(argument) + second_function_with_long_name(arg),
}

# The opening line would be too long with an optional parenthesis.
some_object.some_attribute_with_a_very_long_name["some_key_with_a_very_long_name_too"] = first(arg) + second(arg)

# Binary operations inside brackets are unchanged.
call(first_function_with_long_name(argument) + second_function_with_long_name(argument), x)

# Short operations stay on one line.
small = f(x) + g(y)

# output

# Regression tests for https://github.com/psf/black/issues/4455.
value = (
    get_value_from_a_kinda_long_function_that_is_even_longer()
    + max(offset, threshold)
)


class SomeClass:
    def some_method(value):
        return (
            self.another_method(value - max_size)
            + self.another_method(min_size - value)
        )


# Chains of three or more operands already split before every operator.
value = (
    get_value_from_a_kinda_long_function()
    + previous_values[-1]
    + max(offset, threshold)
)


# Tuples are not binary operations.
def prepare_batch(batch, device, non_blocking):
    x, y = batch["image"].to(device, non_blocking=non_blocking), batch["label"].to(
        device, non_blocking=non_blocking
    )


# Every arithmetic and bitwise binary operator is split the same way.
difference = (
    first_function_with_long_name(argument)
    - second_function_with_long_name(arg)
)
product = (
    first_function_with_long_name(argument)
    * second_function_with_long_name(argument)
)
quotient = (
    first_function_with_long_name(argument)
    / second_function_with_long_name(argument)
)
floor_quotient = (
    first_function_with_long_name(argument)
    // second_function_with_long_name(arg)
)
remainder = (
    first_function_with_long_name(argument)
    % second_function_with_long_name(argument)
)
matrix_product = (
    first_function_with_long_name(argument)
    @ second_function_with_long_name(arg)
)
power = (
    first_function_with_long_name(argument)
    ** second_function_with_long_name(argument)
)
left_shift = (
    first_function_with_long_name(argument)
    << second_function_with_long_name(arg)
)
right_shift = (
    first_function_with_long_name(argument)
    >> second_function_with_long_name(arg)
)
bitwise_and = (
    first_function_with_long_name(argument)
    & second_function_with_long_name(arg)
)
bitwise_xor = (
    first_function_with_long_name(argument)
    ^ second_function_with_long_name(arg)
)
bitwise_or = (
    first_function_with_long_name(argument)
    | second_function_with_long_name(arg)
)

# This includes string formatting with a tuple of arguments.
message = (
    "Something went wrong with %s while processing the request %s"
    % (first, second)
)

# Operands may contain attribute access, subscripts, unary operators, and operators
# with a higher priority.
total = (
    self.first_attribute.compute(first_argument)
    + self.second_attribute[some_key](arg)
)
total = (
    -first_function_with_long_name(argument)
    + second_function_with_long_name(argument)
)
total = (
    first_value * first_function_with_long_name(argument)
    + second_function_name(arg)
)


async def main():
    result = (
        await first_function_with_long_name(argument)
        + second_function_name(argument)
    )


# Other statements with optional parentheses are split the same way.
def f():
    if (
        first_function_with_long_name(argument)
        + second_function_with_long_name(argument)
    ):
        return (
            first_function_with_long_name(argument)
            + second_function_with_long_name(arg)
        )
    for item in (
        first_function_with_long_name(argument)
        + second_function_with_long_name(arg)
    ):
        pass


some_dict["with_a_long_key"] = (
    some_function_name(first_argument)
    + other_function(second)
)
some_object.some_attribute_with_a_very_long_name["some_key_with_a_long_name"] = (
    first(arg)
    + second(arg)
)

# Comments on an operand stay attached and formatting remains stable.
commented_left = (
    first_function_with_long_name(argument)  # first
    + second_function_with_long_name(argument)
)
commented_right = (
    first_function_with_long_name(argument)
    + second_function_with_long_name(argument)  # second
)
comment_in_operand = (
    first_function_with_long_name(argument)  # comment
    + second_function_with_long_name(argument)
)

# Operands that would still be split keep the existing formatting.
long_left = first_function_with_a_really_long_name(
    first_argument, second_argument, third_argument_value
) + f(x)
long_right = f(x) + first_function_with_a_really_long_name(
    first_argument, second_argument, third_argument_value
)
magic_trailing_comma = first_function(
    argument,
) + second_function_with_a_long_name(argument_value)
multiline_string = """
text
""" + second_function_with_a_long_name(
    argument_value, another_argument_value, third_one
)

# Splitting before the operator would misrepresent precedence.
negation = not some_function_with_long_name(argument) + other_function_with_long_name(
    arg
)
handler = lambda event: process_the_event_with_long_name(event) + finalize_event(
    event_id
)

# Comparisons and boolean operations are unchanged.
assert some_function_with_a_long_name(argument_one) == other_function_long_name(
    argument
)
condition = some_function_with_a_long_name(argument_one) and other_function_long_name(
    arg
)

# Operations that already keep their optional parentheses are unchanged.
some_variable_name = (
    some_long_function_name(argument_one) + another_long_variable_name_here
)
mapping = {
    "some_key": (
        first_function_with_long_name(argument) + second_function_with_long_name(arg)
    ),
}

# The opening line would be too long with an optional parenthesis.
some_object.some_attribute_with_a_very_long_name[
    "some_key_with_a_very_long_name_too"
] = first(arg) + second(arg)

# Binary operations inside brackets are unchanged.
call(
    first_function_with_long_name(argument) + second_function_with_long_name(argument),
    x,
)

# Short operations stay on one line.
small = f(x) + g(y)
