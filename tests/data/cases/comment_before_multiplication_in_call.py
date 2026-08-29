# Regression test for https://github.com/psf/black/issues/3713.
my_func(
    arg1=1,
    arg2=[
        func_call(
            # Comment.
            [MyClass(arg1, arg2)] * 10000
        ),
    ],
)

# A single arithmetic/bitwise operator should stay collapsed too.
func_call(
    # Comment.
    a + b
)

# But if the result still doesn't fit, it still needs to split around the
# operator (just without the comment forcing it unnecessarily).
func_call(
    # Comment.
    [MyClass(arg1, arg2)] * some_extremely_long_multiplier_that_certainly_does_not_fit_at_all_here
)

# output

# Regression test for https://github.com/psf/black/issues/3713.
my_func(
    arg1=1,
    arg2=[
        func_call(
            # Comment.
            [MyClass(arg1, arg2)] * 10000
        ),
    ],
)

# A single arithmetic/bitwise operator should stay collapsed too.
func_call(
    # Comment.
    a + b
)

# But if the result still doesn't fit, it still needs to split around the
# operator (just without the comment forcing it unnecessarily).
func_call(
    # Comment.
    [MyClass(arg1, arg2)]
    * some_extremely_long_multiplier_that_certainly_does_not_fit_at_all_here
)
