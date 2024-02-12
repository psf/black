# flags: --unstable
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


class Random:
    def func():
        random_service.status.active_states.inactive = (
            make_new_top_level_state_from_dict(
                {
                    "topLevelBase": {
                        "secondaryBase": {
                            "timestamp": 1234,
                            "latitude": 1,
                            "longitude": 2,
                            "actionTimestamp": Timestamp(
                                seconds=1530584000, nanos=0
                            ).ToJsonString(),
                        }
                    },
                }
            )
        )


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


class Random:
    def func():
        random_service.status.active_states.inactive = (
            make_new_top_level_state_from_dict({
                "topLevelBase": {
                    "secondaryBase": {
                        "timestamp": 1234,
                        "latitude": 1,
                        "longitude": 2,
                        "actionTimestamp": (
                            Timestamp(seconds=1530584000, nanos=0).ToJsonString()
                        ),
                    }
                },
            })
        )
