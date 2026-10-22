# flags: --preview
x = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
    # Comment between calls
    .g()
)
y = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
    # Comment between calls
    .g()
    .h()
)

# A comment before the chain must not trigger the new method-chain split.
z = (
    # Comment before the chain
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
)
w = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
        # Comment inside the call
    ).f()
)

# output
x = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    )
    .f()
    # Comment between calls
    .g()
)
y = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    )
    .f()
    # Comment between calls
    .g()
    .h()
)

# A comment before the chain must not trigger the new method-chain split.
z = (
    # Comment before the chain
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    ).f()
)
w = very_long_function_name_with_many_arguments(
    100,
    200,
    300,
    400,
    500,
    600,
    700,
    800,
    900,
    1000,
    # Comment inside the call
).f()
