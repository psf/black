# flags: --minimum-version=3.12
def func  [T ](): pass
async def func [ T ] (): pass
class C[ T ] : pass

def all_in[T   :   int,U : (bytes, str),*   Ts,**P](): pass

def really_long[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine](): pass

def even_longer[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine: WhatIfItHadABound](): pass

def it_gets_worse[WhatIsTheLongestTypeVarNameYouCanThinkOfEnoughToMakeBlackSplitThisLine, ItCouldBeGenericOverMultipleTypeVars](): pass

def magic[Trailing, Comma,](): pass

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
