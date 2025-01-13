# flags: --unstable
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    )
}
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    ),
}
x = {
    "foo": bar,
    "foo": bar,
    "foo": (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    ),
}
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxx"
}

my_dict = {
    "something_something":
        r"Lorem ipsum dolor sit amet, an sed convenire eloquentiam \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t",
}

# Function calls as keys
tasks = {
    get_key_name(
        foo,
        bar,
        baz,
    ): src,
    loop.run_in_executor(): src,
    loop.run_in_executor(xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx): src,
    loop.run_in_executor(
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxx
    ): src,
    loop.run_in_executor(): (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    ),
}

# Dictionary comprehensions
tasks = {
    key_name: (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    )
    for src in sources
}
tasks = {key_name: foobar for src in sources}
tasks = {
    get_key_name(
        src,
    ): "foo"
    for src in sources
}
tasks = {
    get_key_name(
        foo,
        bar,
        baz,
    ): src
    for src in sources
}
tasks = {
    get_key_name(): (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    )
    for src in sources
}
tasks = {get_key_name(): foobar for src in sources}


# Delimiters inside the value
def foo():
    def bar():
        x = {
            common.models.DateTimeField: datetime(2020, 1, 31, tzinfo=utc) + timedelta(
                days=i
            ),
        }
        x = {
            common.models.DateTimeField: (
                datetime(2020, 1, 31, tzinfo=utc) + timedelta(days=i)
            ),
        }
        x = {
            "foobar": (123 + 456),
        }
        x = {
            "foobar": (123) + 456,
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
    "xxxxxx":
        xxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxx(
            xxxxxxxxxxxxxx={
                "x":
                    xxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=(
                            xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                            .xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                                xxxxxxxxxxxxx=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                                .xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
                                    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx={
                                        "x": x.xx,
                                        "x": x.x,
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
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    )
}
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    ),
}
x = {
    "foo": bar,
    "foo": bar,
    "foo": (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    ),
}
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxx"
}

my_dict = {
    "something_something": (
        r"Lorem ipsum dolor sit amet, an sed convenire eloquentiam \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
        r"signiferumque, duo ea vocibus consetetur scriptorem. Facer \t"
    ),
}

# Function calls as keys
tasks = {
    get_key_name(
        foo,
        bar,
        baz,
    ): src,
    loop.run_in_executor(): src,
    loop.run_in_executor(xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx): src,
    loop.run_in_executor(
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxx
    ): src,
    loop.run_in_executor(): (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    ),
}

# Dictionary comprehensions
tasks = {
    key_name: (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    )
    for src in sources
}
tasks = {key_name: foobar for src in sources}
tasks = {
    get_key_name(
        src,
    ): "foo"
    for src in sources
}
tasks = {
    get_key_name(
        foo,
        bar,
        baz,
    ): src
    for src in sources
}
tasks = {
    get_key_name(): (
        xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    )
    for src in sources
}
tasks = {get_key_name(): foobar for src in sources}


# Delimiters inside the value
def foo():
    def bar():
        x = {
            common.models.DateTimeField: (
                datetime(2020, 1, 31, tzinfo=utc) + timedelta(days=i)
            ),
        }
        x = {
            common.models.DateTimeField: (
                datetime(2020, 1, 31, tzinfo=utc) + timedelta(days=i)
            ),
        }
        x = {
            "foobar": 123 + 456,
        }
        x = {
            "foobar": (123) + 456,
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
        random_service.status.active_states.inactive = make_new_top_level_state_from_dict({
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
