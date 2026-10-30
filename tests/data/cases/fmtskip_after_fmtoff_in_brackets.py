# `# fmt: skip` on the closing bracket of a `# fmt: off` region, which often ends in a
# comment.

x = [
    # fmt: off
    a,  b  # comment
]  # fmt: skip

x = [
    # fmt: off
    a,  b
    # comment
]  # fmt: skip

x = [
    # fmt: off
    a,  b  # comment
    # fmt: on
]  # fmt: skip

x = [
    # fmt: off
    a  # comment
]  # fmt: skip


class A(
    # fmt: off
    B  # comment
):  # fmt: skip
    pass


class C(
    # fmt: off
    B
):  # fmt: skip
    pass

# output

# `# fmt: skip` on the closing bracket of a `# fmt: off` region, which often ends in a
# comment.

x = [
# fmt: off
    a,  b  # comment
]  # fmt: skip

x = [
# fmt: off
    a,  b
    # comment
]  # fmt: skip

x = [
# fmt: off
    a,  b  # comment
    # fmt: on
]  # fmt: skip

x = [
# fmt: off
    a  # comment
]  # fmt: skip


class A(
# fmt: off
    B  # comment
):  # fmt: skip
    pass


class C(
# fmt: off
    B
):  # fmt: skip
    pass
