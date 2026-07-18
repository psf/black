# flags: --minimum-version=3.12
def inline_comments[
    T,  # a plain type var
    U,  # another one
](x: T) -> U:
    pass


class Leading[
    # a standalone leading comment
    T,
    # comment before U
    U,
]:
    pass


def bound_comment[T: int](x: T) -> T:  # comment after signature
    return x


def bound_comment_inside[
    T: SomeLongBoundNameThatGoesOnAndOn,  # bound has a comment
    U: (int, str, bytes),  # constraint tuple with a comment
](x: T) -> T:
    return x


def comment_forces_explosion[T, U](  # trailing comment on the paren
    x: T,
) -> U:
    pass


def only_comment_no_comma[
    T  # no trailing comma, just a comment
]():
    pass


def star_params_inline[T, *Ts, **P](x: T) -> T:  # fits on one line
    return x

# output

def inline_comments[
    T,  # a plain type var
    U,  # another one
](
    x: T,
) -> U:
    pass


class Leading[
    # a standalone leading comment
    T,
    # comment before U
    U,
]:
    pass


def bound_comment[T: int](x: T) -> T:  # comment after signature
    return x


def bound_comment_inside[
    T: SomeLongBoundNameThatGoesOnAndOn,  # bound has a comment
    U: (int, str, bytes),  # constraint tuple with a comment
](
    x: T,
) -> T:
    return x


def comment_forces_explosion[T, U](  # trailing comment on the paren
    x: T,
) -> U:
    pass


def only_comment_no_comma[T]():  # no trailing comma, just a comment
    pass


def star_params_inline[T, *Ts, **P](x: T) -> T:  # fits on one line
    return x
