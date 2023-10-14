# flags: --preview
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

{
    'xxxxxx':
        xxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxx(
            xxxxxxxxxxxxxx={
                'x':
                    xxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=(
                            xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                            .xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                                xxxxxxxxxxxxx=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                                .xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                                    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx={
                                        'x': x.xx,
                                        'x': x.x,
                                    }))))
            }),
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

{
    "xxxxxx": xxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxx(
        xxxxxxxxxxxxxx={
            "x": xxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=(
                    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                        xxxxxxxxxxxxx=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                            xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx={
                                "x": x.xx,
                                "x": x.x,
                            }
                        )
                    )
                )
            )
        }
    ),
}
