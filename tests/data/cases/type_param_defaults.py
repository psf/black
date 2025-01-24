# flags: --minimum-version=3.13

type A[T=int] = float
type B[*P=int] = float
type C[*Ts=int] = float
type D[*Ts=*int] = float
type D[something_that_is_very_very_very_long=something_that_is_very_very_very_long] = float
type D[*something_that_is_very_very_very_long=*something_that_is_very_very_very_long] = float
type something_that_is_long[something_that_is_long=something_that_is_long] = something_that_is_long

def simple[T=something_that_is_long](short1: int, short2: str, short3: bytes) -> float:
    pass

def longer[something_that_is_long=something_that_is_long](something_that_is_long: something_that_is_long) -> something_that_is_long:
    pass

def trailing_comma1[T=int,](a: str):
    pass

def trailing_comma2[T=int](a: str,):
    pass

# output

type A[T = int] = float
type B[*P = int] = float
type C[*Ts = int] = float
type D[*Ts = *int] = float
type D[
    something_that_is_very_very_very_long = something_that_is_very_very_very_long
] = float
type D[
    *something_that_is_very_very_very_long = *something_that_is_very_very_very_long
] = float
type something_that_is_long[
    something_that_is_long = something_that_is_long
] = something_that_is_long


def simple[
    T = something_that_is_long
](short1: int, short2: str, short3: bytes) -> float:
    pass


def longer[
    something_that_is_long = something_that_is_long
](something_that_is_long: something_that_is_long) -> something_that_is_long:
    pass


def trailing_comma1[
    T = int,
](a: str):
    pass


def trailing_comma2[
    T = int
](a: str,):
    pass
