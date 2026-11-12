# `# fmt: skip` after the last base of a class header that has its own `# fmt: skip`
class A(
    B,  # fmt: skip
):  # fmt: skip
    pass


class A(
    B  # fmt: skip
):  # fmt: skip
    pass


class A(
    B,
    C,  # fmt: skip
):  # fmt: skip
    pass


class A(
    metaclass=M,  # fmt: skip
):  # fmt: skip
    pass


@decorator
class A(
    B,  # fmt: skip
):  # fmt: skip
    x = 1


class Outer:
    class A(
        B,  # fmt: skip
    ):  # fmt: skip
        """Docstring."""
