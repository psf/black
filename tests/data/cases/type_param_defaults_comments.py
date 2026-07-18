# flags: --minimum-version=3.13
type Alias[T = int] = list[T]  # simple default


def default_comment[
    T = int,  # default with a comment
    U = str,  # another default
](x: T) -> U:
    pass


def starred_defaults_inline[*Ts = Unpack, **P = Params](x):  # stays on one line
    ...


def bound_and_default[
    T: Bound = Default,  # both a bound and a default
](x: T) -> T:
    return x


type LongDefault[
    T = SomethingThatIsVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryLong,  # long default
] = list[T]


def mixed[
    T,  # no default
    U = int,  # has a default
](x: T, y: U) -> U:
    return y

# output

type Alias[T = int] = list[T]  # simple default


def default_comment[
    T = int,  # default with a comment
    U = str,  # another default
](
    x: T,
) -> U:
    pass


def starred_defaults_inline[*Ts = Unpack, **P = Params](x):  # stays on one line
    ...


def bound_and_default[
    T: Bound = Default,  # both a bound and a default
](
    x: T,
) -> T:
    return x


type LongDefault[
    T = SomethingThatIsVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryLong,  # long default
] = list[T]


def mixed[
    T,  # no default
    U = int,  # has a default
](
    x: T, y: U
) -> U:
    return y
