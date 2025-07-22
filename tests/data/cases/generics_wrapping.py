# flags: --minimum-version=3.12
def plain[T, B](a: T, b: T) -> T:
    return a

def arg_magic[T, B](a: T, b: T,) -> T:
    return a

def type_param_magic[T, B,](a: T, b: T) -> T:
    return a

def both_magic[T, B,](a: T, b: T,) -> T:
    return a


def plain_multiline[
    T,
    B
](
    a: T,
    b: T
) -> T:
    return a

def arg_magic_multiline[
    T,
    B
](
    a: T,
    b: T,
) -> T:
    return a

def type_param_magic_multiline[
    T,
    B,
](
    a: T,
    b: T
) -> T:
    return a

def both_magic_multiline[
    T,
    B,
](
    a: T,
    b: T,
) -> T:
    return a


def plain_mixed1[
    T,
    B
](a: T, b: T) -> T:
    return a

def plain_mixed2[T, B](
    a: T,
    b: T
) -> T:
    return a

def arg_magic_mixed1[
    T,
    B
](a: T, b: T,) -> T:
    return a

def arg_magic_mixed2[T, B](
    a: T,
    b: T,
) -> T:
    return a

def type_param_magic_mixed1[
    T,
    B,
](a: T, b: T) -> T:
    return a

def type_param_magic_mixed2[T, B,](
    a: T,
    b: T
) -> T:
    return a

def both_magic_mixed1[
    T,
    B,
](a: T, b: T,) -> T:
    return a

def both_magic_mixed2[T, B,](
    a: T,
    b: T,
) -> T:
    return a

def something_something_function[
    T: Model
](param: list[int], other_param: type[T], *, some_other_param: bool = True) -> QuerySet[
    T
]:
    pass


def func[A_LOT_OF_GENERIC_TYPES: AreBeingDefinedHere, LIKE_THIS, AND_THIS, ANOTHER_ONE, AND_YET_ANOTHER_ONE: ThisOneHasTyping](a: T, b: T, c: T, d: T, e: T, f: T, g: T, h: T, i: T, j: T, k: T, l: T, m: T, n: T, o: T, p: T) -> T:
    return a


def with_random_comments[
    Z
    # bye
]():
    return a


def func[
    T,  # comment
    U  # comment
    ,
    Z:  # comment
    int
](): pass


def func[
    T,  # comment but it's long so it doesn't just move to the end of the line
    U  # comment comment comm comm ent ent
    ,
    Z:  # comment ent ent comm comm comment
    int
](): pass


# output
def plain[T, B](a: T, b: T) -> T:
    return a


def arg_magic[T, B](
    a: T,
    b: T,
) -> T:
    return a


def type_param_magic[
    T,
    B,
](
    a: T, b: T
) -> T:
    return a


def both_magic[
    T,
    B,
](
    a: T,
    b: T,
) -> T:
    return a


def plain_multiline[T, B](a: T, b: T) -> T:
    return a


def arg_magic_multiline[T, B](
    a: T,
    b: T,
) -> T:
    return a


def type_param_magic_multiline[
    T,
    B,
](
    a: T, b: T
) -> T:
    return a


def both_magic_multiline[
    T,
    B,
](
    a: T,
    b: T,
) -> T:
    return a


def plain_mixed1[T, B](a: T, b: T) -> T:
    return a


def plain_mixed2[T, B](a: T, b: T) -> T:
    return a


def arg_magic_mixed1[T, B](
    a: T,
    b: T,
) -> T:
    return a


def arg_magic_mixed2[T, B](
    a: T,
    b: T,
) -> T:
    return a


def type_param_magic_mixed1[
    T,
    B,
](
    a: T, b: T
) -> T:
    return a


def type_param_magic_mixed2[
    T,
    B,
](
    a: T, b: T
) -> T:
    return a


def both_magic_mixed1[
    T,
    B,
](
    a: T,
    b: T,
) -> T:
    return a


def both_magic_mixed2[
    T,
    B,
](
    a: T,
    b: T,
) -> T:
    return a


def something_something_function[T: Model](
    param: list[int], other_param: type[T], *, some_other_param: bool = True
) -> QuerySet[T]:
    pass


def func[
    A_LOT_OF_GENERIC_TYPES: AreBeingDefinedHere,
    LIKE_THIS,
    AND_THIS,
    ANOTHER_ONE,
    AND_YET_ANOTHER_ONE: ThisOneHasTyping,
](
    a: T,
    b: T,
    c: T,
    d: T,
    e: T,
    f: T,
    g: T,
    h: T,
    i: T,
    j: T,
    k: T,
    l: T,
    m: T,
    n: T,
    o: T,
    p: T,
) -> T:
    return a


def with_random_comments[
    Z
    # bye
]():
    return a


def func[T, U, Z: int]():  # comment  # comment  # comment
    pass


def func[
    T,  # comment but it's long so it doesn't just move to the end of the line
    U,  # comment comment comm comm ent ent
    Z: int,  # comment ent ent comm comm comment
]():
    pass
