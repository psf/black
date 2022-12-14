my_dict = {
    "something_something":
        r"Lorem ipsum dolor sit amet, an sed convenire eloquentiam \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t",
}

my_dict = {
    "a key in my dict": a_very_long_variable * and_a_very_long_function_call() / 100000.0
}

my_dict = {
    "a key in my dict": a_very_long_variable * and_a_very_long_function_call() * and_another_long_func() / 100000.0
}

my_dict = {
    "a key in my dict": MyClass.some_attribute.first_call().second_call().third_call(some_args="some value")
}

dict_with_lambda_values = {
    "join": lambda j: (
        f"{j.__class__.__name__}({some_function_call(j.left)}, "
        f"{some_function_call(j.right)})"
    ),
}


# output


my_dict = {
    "something_something": (
        r"Lorem ipsum dolor sit amet, an sed convenire eloquentiam \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
    ),
}

my_dict = {
    "a key in my dict": (
        a_very_long_variable * and_a_very_long_function_call() / 100000.0
    )
}

my_dict = {
    "a key in my dict": (
        a_very_long_variable
        * and_a_very_long_function_call()
        * and_another_long_func()
        / 100000.0
    )
}

my_dict = {
    "a key in my dict": (
        MyClass.some_attribute.first_call()
        .second_call()
        .third_call(some_args="some value")
    )
}

dict_with_lambda_values = {
    "join": (
        lambda j: (
            f"{j.__class__.__name__}({some_function_call(j.left)}, "
            f"{some_function_call(j.right)})"
        )
    ),
}
