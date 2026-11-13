# flags: --preview
# A `# fmt: off` without `# fmt: on` inside brackets lasts until the closing bracket,
# also when the brackets hold a single name, number or string. The cases that still
# crash without --preview are in test_fmt_off_without_fmt_on_before_single_item.

print(
    # fmt: off
    a
)
# fmt: on
y  =  1

f(
    # fmt: off
    'a'
      # comment
)


class A(
    # fmt: off
    B
):
    x  =  1


def f(
    # fmt: off
    a
):
    return  None


# With `# fmt: skip` on the closing bracket

x = [
    # fmt: off
    a  # comment
]  # fmt: skip


class C(
    # fmt: off
    B  # comment
):  # fmt: skip
    pass


class D(
    # fmt: off
    B
):  # fmt: skip
    pass

# output

# A `# fmt: off` without `# fmt: on` inside brackets lasts until the closing bracket,
# also when the brackets hold a single name, number or string. The cases that still
# crash without --preview are in test_fmt_off_without_fmt_on_before_single_item.

print(
    # fmt: off
    a
)
# fmt: on
y = 1

f(
    # fmt: off
    'a'
      # comment
)


class A(
    # fmt: off
    B
):
    x = 1


def f(
    # fmt: off
    a
):
    return None


# With `# fmt: skip` on the closing bracket

x = [
# fmt: off
    a  # comment
]  # fmt: skip


class C(
# fmt: off
    B  # comment
):  # fmt: skip
    pass


class D(
# fmt: off
    B
):  # fmt: skip
    pass
