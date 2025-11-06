def foo():
    pass


# comment 1  # fmt: skip
# comment 2

v = (
    foo_dict  # fmt: skip
    .setdefault("a", {})
    .setdefault("b", {})
    .setdefault("c", {})
    .setdefault("d", {})
    .setdefault("e", {})
)

t = (
    {"foo": "very long string", "bar": "another very long string", "baz": "we should run out of space by now"},  # fmt: skip
    {"foo": "bar"},
)

t = (
    {
        "foo": "very long string",
        "bar": "another very long string",
        "baz": "we should run out of space by now",
    },  # fmt: skip
    {"foo": "bar"},
)
