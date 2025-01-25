# flags: --minimum-version=3.12 --skip-magic-trailing-comma
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


# output
def plain[T, B](a: T, b: T) -> T:
    return a


def arg_magic[T, B](a: T, b: T) -> T:
    return a


def type_param_magic[T, B](a: T, b: T) -> T:
    return a


def both_magic[T, B](a: T, b: T) -> T:
    return a


def plain_multiline[T, B](a: T, b: T) -> T:
    return a


def arg_magic_multiline[T, B](a: T, b: T) -> T:
    return a


def type_param_magic_multiline[T, B](a: T, b: T) -> T:
    return a


def both_magic_multiline[T, B](a: T, b: T) -> T:
    return a


def plain_mixed1[T, B](a: T, b: T) -> T:
    return a


def plain_mixed2[T, B](a: T, b: T) -> T:
    return a


def arg_magic_mixed1[T, B](a: T, b: T) -> T:
    return a


def arg_magic_mixed2[T, B](a: T, b: T) -> T:
    return a


def type_param_magic_mixed1[T, B](a: T, b: T) -> T:
    return a


def type_param_magic_mixed2[T, B](a: T, b: T) -> T:
    return a


def both_magic_mixed1[T, B](a: T, b: T) -> T:
    return a


def both_magic_mixed2[T, B](a: T, b: T) -> T:
    return a
