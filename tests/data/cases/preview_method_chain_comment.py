# flags: --preview
x = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
    # Comment between calls
    .g()
)
x = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
    # Comment between calls
    # second comment
    .g()
)
y = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
    # Comment between calls
    .g()
    .h()
)
y = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
    # Comment between calls
    .g()
    # Comment between calls
    .h()
)
y = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
    # Comment between calls
    .g()
    # Comment between call and attr
    .h
    # Comment between attr and call
    .i()
)
y = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)
    # Comment before first chained call
    .f()
    .g()
)
y = (
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).
    # Comment after dot
    f()
    .g()
)

z = (
    # Comment before the chain doesn't trigger
    very_long_function_name_with_many_arguments(100, 200, 300, 400, 500, 600, 700, 800, 900, 1000).f()
)
w = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
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
x = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    )
    .f()
    # Comment between calls
    # second comment
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
y = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    )
    .f()
    # Comment between calls
    .g()
    # Comment between calls
    .h()
)
y = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    )
    .f()
    # Comment between calls
    .g()
    # Comment between call and attr
    .h
    # Comment between attr and call
    .i()
)
y = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    )
    # Comment before first chained call
    .f()
    .g()
)
y = (
    very_long_function_name_with_many_arguments(
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    )
    .
    # Comment after dot
    f()
    .g()
)

z = (
    # Comment before the chain doesn't trigger
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
