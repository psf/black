# flags: --minimum-version=3.14
# `# fmt: off` in the expression of an f-string field with `=` or a t-string field.
# Python keeps the source there as text, so the comment stays where it is.

x = f"{a
    # fmt: off
=}"

x = f"{a + b  # comment
    # fmt: off
    =  }"

x = f"{a=
    # fmt: off
    !r:>10}"

x = f"{[a,
        # fmt: off
        b]=}"

x = f"{f'{b
    # fmt: off
    + c}'=}"


def f():
    return f"""{
        # fmt: off
        a,  b
    =}"""


x = t"{a
    # fmt: off
    + b}"

x = t"{a
    # fmt: off
    !r}"
