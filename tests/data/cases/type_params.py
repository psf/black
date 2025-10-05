# flags: --minimum-version=3.12
def func  [T ](): pass
async def func [ T ] (): pass
class C[ T ] : pass

def all_in[T   :   int,U : (bytes, str),*   Ts,**P](): pass

def really_long[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine](): pass

def even_longer[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine: WhatIfItHadABound](): pass

def it_gets_worse[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine, ItCouldBeGenericOverMultipleTypeVars](): pass

def magic[Trailing, Comma,](): pass

def weird_syntax[T: lambda: 42, U: a or b](): pass

def name_3[name_0: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa if aaaaaaaaaaa else name_3](): pass

def f1[T: (int, str)](a,): pass

def f2[T: (int, str)](a: int, b,): pass

def g1[T: (int,)](a,): pass

def g2[T: (int, str, bytes)](a,): pass

def g3[T: ((int, str), (bytes,))](a,): pass

def g4[T: (int, (str, bytes))](a,): pass

def g5[T: ((int,),)](a: int, b,): pass
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


def weird_syntax[T: lambda: 42, U: a or b]():
    pass


def name_3[
    name_0: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa if aaaaaaaaaaa else name_3
]():
    pass


def f1[T: (int, str)](
    a,
):
    pass


def f2[T: (int, str)](
    a: int,
    b,
):
    pass


def g1[T: (int,)](
    a,
):
    pass


def g2[T: (int, str, bytes)](
    a,
):
    pass


def g3[T: ((int, str), (bytes,))](
    a,
):
    pass


def g4[T: (int, (str, bytes))](
    a,
):
    pass


def g5[T: ((int,),)](
    a: int,
    b,
):
    pass