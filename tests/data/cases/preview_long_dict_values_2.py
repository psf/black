# flags: --unstable

x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    )
}
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx",
}
x = {
    "foo": (bar),
    "foo": bar,
    "foo": xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx,
}
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxx"
    )
}

# Function calls as keys
tasks = {
    get_key_name(foo, bar, baz,): src,
    loop.run_in_executor(): src,
    loop.run_in_executor(xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx): src,
    loop.run_in_executor(xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxx): src,
    loop.run_in_executor(): xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
}

# Dictionary comprehensions
tasks = {
    key_name: xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    for src in sources
}
tasks = {key_name: foobar for src in sources}
tasks = {get_key_name(foo, bar, baz,): src for src in sources}
tasks = {
    get_key_name(): xx_xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxxxxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx
    for src in sources
}
tasks = {
    get_key_name(): foobar
    for src in sources
}

# Delimiters inside the value
def foo():
    def bar():
        x = {
            common.models.DateTimeField: (
                datetime(2020, 1, 31, tzinfo=utc) + timedelta(days=i)
            ),
        }
        x = {
            common.models.DateTimeField: datetime(2020, 1, 31, tzinfo=utc) + timedelta(
                days=i
            ),
        }
        x = {
            "foobar": (
                123 + 456
            ),
        }


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
