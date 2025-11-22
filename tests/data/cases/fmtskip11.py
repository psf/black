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
