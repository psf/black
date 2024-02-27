# flags: --minimum-version=3.12
def func  [T ](): pass
async def func [ T ] (): pass
class C[ T ] : pass

def all_in[T   :   int,U : (bytes, str),*   Ts,**P](): pass

def really_long[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine](): pass

def even_longer[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine: WhatIfItHadABound](): pass

def it_gets_worse[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine, ItCouldBeGenericOverMultipleTypeVars](): pass

def magic[Trailing, Comma,](): pass

# Combinations of type params, function params and return types
def func00[T](a): pass

def func01[T](a,): pass

def func10[T,](a): pass

def func11[T,](a,): pass

def func000[T](a) -> list[A, B]: pass

def func010[T](a,) -> list[A, B]: pass

def func100[T,](a) -> list[A, B]: pass

def func110[T,](a,) -> list[A, B]: pass

def func001[T](a) -> list[A, B,]: pass

def func011[T](a,) -> list[A, B,]: pass

def func101[T,](a) -> list[A, B,]: pass

def func111[T,](a,) -> list[A, B,]: pass

def long_func_params[T](aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb): pass

# output


def func[T]():
    pass


async def func[T]():
    pass


class C[T]:
    pass


def all_in[T: int, U: (bytes, str), *Ts, **P]():
    pass


def really_long[
    WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine
]():
    pass


def even_longer[
    WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine: WhatIfItHadABound
]():
    pass


def it_gets_worse[
    WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine,
    ItCouldBeGenericOverMultipleTypeVars,
]():
    pass


def magic[
    Trailing,
    Comma,
]():
    pass


# Combinations of type params, function params and return types
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


def long_func_params[T](
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,
    bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb,
):
    pass
