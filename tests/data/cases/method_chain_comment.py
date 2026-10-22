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

# output
x = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    ).f()
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
