my_func(
    arg1=1,
    arg2=[
        func_call(
            # Comment.
            [MyClass(arg1, arg2)] * 10000
        ),
    ],
)

result = func_call(
    # Comment.
    value * 10000
)

result = func_call(
    # Comment.
    value + other_value
)


# output

my_func(
    arg1=1,
    arg2=[
        func_call(
            # Comment.
            [MyClass(arg1, arg2)] * 10000
        ),
    ],
)

result = func_call(
    # Comment.
    value * 10000
)

result = func_call(
    # Comment.
    value + other_value
)
