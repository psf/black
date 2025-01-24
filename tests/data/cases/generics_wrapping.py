# flags: --minimum-version=3.12 --preview
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
](a: T, b: T) -> T:
    return a


def both_magic[
    T,
    B,
](a: T, b: T,) -> T:
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
](a: T, b: T) -> T:
    return a


def both_magic_multiline[
    T,
    B,
](a: T, b: T,) -> T:
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
](a: T, b: T) -> T:
    return a


def type_param_magic_mixed2[
    T,
    B,
](a: T, b: T) -> T:
    return a


def both_magic_mixed1[
    T,
    B,
](a: T, b: T,) -> T:
    return a


def both_magic_mixed2[
    T,
    B,
](a: T, b: T,) -> T:
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
