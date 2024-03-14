# flags: --preview --minimum-version=3.12

# https://github.com/psf/black/issues/3929
def sum_backward[T: SupportedDataTypes](a: Tensor[T], grad: Tensor[T]) -> dict[Tensor[T], Tensor[T]]: ...


# https://github.com/psf/black/issues/4071
def func[T](a: T, b: T,) -> T: return a + b

# Combinations of type params, function params and return types with trailing commas
def func0(a): pass

def func1(a,): pass

def func00[T](a): pass

def func01[T](a,): pass

def func10[T,](a): pass

def func11[T,](a,): pass

def func0_0(a) -> List[A, B]: pass

def func0_1(a) -> List[A, B,]: pass

def func1_0(a,) -> List[A, B]: pass

def func1_1(a,) -> List[A, B,]: pass

def func000[T](a) -> list[A, B]: pass

def func010[T](a,) -> list[A, B]: pass

def func100[T,](a) -> list[A, B]: pass

def func110[T,](a,) -> list[A, B]: pass

def func001[T](a) -> list[A, B,]: pass

def func011[T](a,) -> list[A, B,]: pass

def func101[T,](a) -> list[A, B,]: pass

def func111[T,](a,) -> list[A, B,]: pass

def long_func_params[T, U](aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb) -> R | S: pass

def long_type_params[TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT, UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU](a, b) -> R | S: pass

def long_return_type[T, U](a, b) -> RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR | SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS: pass

def long_func_param2[T, U](aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb) -> R | S: pass

def long_type_param2[TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU](a, b) -> R | S: pass

def long_return_type2[T, U](a, b) -> RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS: pass

# output

# https://github.com/psf/black/issues/3929
def sum_backward[T: SupportedDataTypes](
    a: Tensor[T], grad: Tensor[T]
) -> dict[Tensor[T], Tensor[T]]: ...


# https://github.com/psf/black/issues/4071
def func[T](
    a: T,
    b: T,
) -> T:
    return a + b


# Combinations of type params, function params and return types with trailing commas
def func0(a):
    pass


def func1(
    a,
):
    pass


def func00[T](a):
    pass


def func01[T](
    a,
):
    pass


def func10[
    T,
](a):
    pass


def func11[
    T,
](
    a,
):
    pass


def func0_0(a) -> List[A, B]:
    pass


def func0_1(a) -> List[
    A,
    B,
]:
    pass


def func1_0(
    a,
) -> List[A, B]:
    pass


def func1_1(
    a,
) -> List[
    A,
    B,
]:
    pass


def func000[T](a) -> list[A, B]:
    pass


def func010[T](
    a,
) -> list[A, B]:
    pass


def func100[
    T,
](a) -> list[A, B]:
    pass


def func110[
    T,
](
    a,
) -> list[A, B]:
    pass


def func001[T](a) -> list[
    A,
    B,
]:
    pass


def func011[T](
    a,
) -> list[
    A,
    B,
]:
    pass


def func101[
    T,
](a) -> list[
    A,
    B,
]:
    pass


def func111[
    T,
](
    a,
) -> list[
    A,
    B,
]:
    pass


def long_func_params[T, U](
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,
    bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb,
) -> R | S:
    pass


def long_type_params[
    TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT,
    UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU,
](a, b) -> R | S:
    pass


def long_return_type[T, U](a, b) -> (
    RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
    | SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
):
    pass


def long_func_param2[T, U](
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb,
) -> R | S:
    pass


def long_type_param2[
    TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU
](a, b) -> R | S:
    pass


def long_return_type2[T, U](
    a, b
) -> RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS:
    pass
