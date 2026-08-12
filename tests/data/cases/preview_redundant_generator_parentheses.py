# flags: --preview

any((x for x in items))
service.consume((item for group in groups for item in group if item))
factory((item for item in iterable))()

any((
    this_very_long_method_name(obj) or another_long_method_name(obj)
    for obj in this_iterable
))

# Existing comment handling may keep the generator parentheses visible.
any((
    long_expression_that_exceeds_the_configured_line_length_limit_value  # inline comment
    for item in iterable
))

# Parentheses are required when the generator is not the sole argument.
next((item for item in iterable), None)
enumerate((item for item in iterable), start=10)
consume((item for item in iterable),)
consume(*(item for item in iterable))
consume(generator=(item for item in iterable))

# output

any(x for x in items)
service.consume(item for group in groups for item in group if item)
factory(item for item in iterable)()

any(
    this_very_long_method_name(obj) or another_long_method_name(obj)
    for obj in this_iterable
)

# Existing comment handling may keep the generator parentheses visible.
any(
    (
        long_expression_that_exceeds_the_configured_line_length_limit_value  # inline comment
        for item in iterable
    )
)

# Parentheses are required when the generator is not the sole argument.
next((item for item in iterable), None)
enumerate((item for item in iterable), start=10)
consume(
    (item for item in iterable),
)
consume(*(item for item in iterable))
consume(generator=(item for item in iterable))
