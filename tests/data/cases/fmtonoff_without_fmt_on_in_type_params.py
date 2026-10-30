# flags: --minimum-version=3.12
# Type parameters are direct children of their brackets. A `# fmt: off` without
# `# fmt: on` before them still ends at the closing bracket.

def f[
    # fmt: off
    T,  B,
](a,): pass


class C[
    # fmt: off
    T,  B
]:
    x  =  1


type X[
    # fmt: off
    T
] = int

# output

# Type parameters are direct children of their brackets. A `# fmt: off` without
# `# fmt: on` before them still ends at the closing bracket.


def f[
    # fmt: off
    T,  B,
](
    a,
):
    pass


class C[
    # fmt: off
    T,  B
]:
    x = 1


type X[
    # fmt: off
    T
] = int
