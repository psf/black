# flags: --preview

if isinstance(very_very_very_very_very_very_long_expression, Sequence) and not isinstance(very_very_very_very_very_very_long_expression, str):
    pass

if first_condition:
    pass
elif matches_very_very_very_very_very_very_long_expression(first_value) or matches_very_very_very_very_very_very_long_expression(second_value):
    pass

while is_ready_very_very_very_very_very_very_long_expression(first_value) and not is_finished_very_very_very_very_very_long_expression(second_value):
    pass

# Short conditions do not need parentheses.
if check(first) and check(second):
    pass

# A condition containing only one call still splits the call.
if check_very_very_very_very_very_very_very_very_very_very_long_expression(first, second):
    pass

# Boolean operators nested in a call do not make the condition a boolean expression.
if check_very_very_very_very_very_very_very_very_very_very_long_expression(first and second):
    pass

# Boolean operators nested in explicit parentheses do not affect the outer condition.
if check_very_very_very_very_very_very_very_very_very_long_expression((first and second)):
    pass

# A trailing comma still explodes the call normally.
if enabled and check_very_very_very_very_very_very_very_very_long_expression(first, second,):
    pass

# The split preference is limited to conditional statements.
result = check_very_very_very_very_very_long_expression(first) and check_very_very_very_very_very_long_expression(second)

# output

if (
    isinstance(very_very_very_very_very_very_long_expression, Sequence)
    and not isinstance(very_very_very_very_very_very_long_expression, str)
):
    pass

if first_condition:
    pass
elif (
    matches_very_very_very_very_very_very_long_expression(first_value)
    or matches_very_very_very_very_very_very_long_expression(second_value)
):
    pass

while (
    is_ready_very_very_very_very_very_very_long_expression(first_value)
    and not is_finished_very_very_very_very_very_long_expression(second_value)
):
    pass

# Short conditions do not need parentheses.
if check(first) and check(second):
    pass

# A condition containing only one call still splits the call.
if check_very_very_very_very_very_very_very_very_very_very_long_expression(
    first, second
):
    pass

# Boolean operators nested in a call do not make the condition a boolean expression.
if check_very_very_very_very_very_very_very_very_very_very_long_expression(
    first and second
):
    pass

# Boolean operators nested in explicit parentheses do not affect the outer condition.
if check_very_very_very_very_very_very_very_very_very_long_expression(
    (first and second)
):
    pass

# A trailing comma still explodes the call normally.
if (
    enabled
    and check_very_very_very_very_very_very_very_very_long_expression(
        first,
        second,
    )
):
    pass

# The split preference is limited to conditional statements.
result = check_very_very_very_very_very_long_expression(
    first
) and check_very_very_very_very_very_long_expression(second)
