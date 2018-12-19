from typing import Any, Tuple


def f(
    a,  # type: int
):
    pass


# test type comments
def f(a, b, c, d, e, f, g, h, i):
    # type: (int, int, int, int, int, int, int, int, int) -> None
    pass


def f(
    a,  # type: int
    b,  # type: int
    c,  # type: int
    d,  # type: int
    e,  # type: int
    f,  # type: int
    g,  # type: int
    h,  # type: int
    i,  # type: int
):
    # type: (...) -> None
    pass


def f(
    arg,  # type: int
    *args,  # type: *Any
    default=False,  # type: bool
    **kwargs,  # type: **Any
):
    # type: (...) -> None
    pass


def f(
    a,  # type: int
    b,  # type: int
    c,  # type: int
    d,  # type: int
):
    # type: (...) -> None

    element = 0  # type: int
    another_element = 1  # type: float
    another_element_with_long_name = 2  # type: int
    another_really_really_long_element_with_a_unnecessarily_long_name_to_describe_what_it_does_enterprise_style = (
        3
    )  # type: int

    tup = (
        another_element,  # type: int
        another_really_really_long_element_with_a_unnecessarily_long_name_to_describe_what_it_does_enterprise_style,  # type: int
    )  # type: Tuple[int, int]

    a = (
        element
        + another_element
        + another_element_with_long_name
        + element
        + another_element
        + another_element_with_long_name
    )  # type: int
