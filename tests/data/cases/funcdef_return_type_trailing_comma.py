# flags: --preview --minimum-version=3.10
# normal, short, function definition
def foo(a, b) -> tuple[int, float]: ...


# normal, short, function definition w/o return type
def foo(a, b): ...


# no splitting
def foo(a: A, b: B) -> list[p, q]:
    pass


# magic trailing comma in param list
def foo(a, b,): ...


# magic trailing comma in nested params in param list
def foo(a, b: tuple[int, float,]): ...


# magic trailing comma in return type, no params
def a() -> tuple[
    a,
    b,
]: ...


# magic trailing comma in return type, params
def foo(a: A, b: B) -> list[
    p,
    q,
]:
    pass


# magic trailing comma in param list and in return type
def foo(
    a: a,
    b: b,
) -> list[
    a,
    a,
]:
    pass


# long function definition, param list is longer
def aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(
    bbbbbbbbbbbbbbbbbb,
) -> cccccccccccccccccccccccccccccc: ...


# long function definition, return type is longer
# this should maybe split on rhs?
def aaaaaaaaaaaaaaaaa(bbbbbbbbbbbbbbbbbb) -> list[
    Ccccccccccccccccccccccccccccccccccccccccccccccccccc, Dddddd
]: ...


# long return type, no param list
def foo() -> list[
    Loooooooooooooooooooooooooooooooooooong,
    Loooooooooooooooooooong,
    Looooooooooooong,
]: ...


# long function name, no param list, no return value
def thiiiiiiiiiiiiiiiiiis_iiiiiiiiiiiiiiiiiiiiiiiiiiiiiis_veeeeeeeeeeeeeeeeeeeeeeery_looooooong():
    pass


# long function name, no param list
def thiiiiiiiiiiiiiiiiiis_iiiiiiiiiiiiiiiiiiiiiiiiiiiiiis_veeeeeeeeeeeeeeeeeeeeeeery_looooooong() -> (
    list[int, float]
): ...


# long function name, no return value
def thiiiiiiiiiiiiiiiiiis_iiiiiiiiiiiiiiiiiiiiiiiiiiiiiis_veeeeeeeeeeeeeeeeeeeeeeery_looooooong(
    a, b
): ...


# unskippable type hint (??)
def foo(a) -> list[aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa]:  # type: ignore
    pass


def foo(a) -> list[
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
]:  # abpedeifnore
    pass

def foo(a, b: list[Bad],): ... # type: ignore

# don't lose any comments (no magic)
def foo( # 1
    a, # 2
    b) -> list[ # 3
               a, # 4
               b]: # 5
        ... # 6


# don't lose any comments (param list magic)
def foo( # 1
    a, # 2
    b,) -> list[ # 3
               a, # 4
               b]: # 5
        ... # 6


# don't lose any comments (return type magic)
def foo( # 1
    a, # 2
    b) -> list[ # 3
               a, # 4
               b,]: # 5
        ... # 6


# don't lose any comments (both magic)
def foo( # 1
    a, # 2
    b,) -> list[ # 3
               a, # 4
               b,]: # 5
        ... # 6

# real life example
def SimplePyFn(
    context: hl.GeneratorContext,
    buffer_input: Buffer[UInt8, 2],
    func_input: Buffer[Int32, 2],
    float_arg: Scalar[Float32],
    offset: int = 0,
) -> tuple[
    Buffer[UInt8, 2],
    Buffer[UInt8, 2],
]: ...
# output
# normal, short, function definition
def foo(a, b) -> tuple[int, float]: ...


# normal, short, function definition w/o return type
def foo(a, b): ...


# no splitting
def foo(a: A, b: B) -> list[p, q]:
    pass


# magic trailing comma in param list
def foo(
    a,
    b,
): ...


# magic trailing comma in nested params in param list
def foo(
    a,
    b: tuple[
        int,
        float,
    ],
): ...


# magic trailing comma in return type, no params
def a() -> tuple[
    a,
    b,
]: ...


# magic trailing comma in return type, params
def foo(a: A, b: B) -> list[
    p,
    q,
]:
    pass


# magic trailing comma in param list and in return type
def foo(
    a: a,
    b: b,
) -> list[
    a,
    a,
]:
    pass


# long function definition, param list is longer
def aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(
    bbbbbbbbbbbbbbbbbb,
) -> cccccccccccccccccccccccccccccc: ...


# long function definition, return type is longer
# this should maybe split on rhs?
def aaaaaaaaaaaaaaaaa(
    bbbbbbbbbbbbbbbbbb,
) -> list[Ccccccccccccccccccccccccccccccccccccccccccccccccccc, Dddddd]: ...


# long return type, no param list
def foo() -> list[
    Loooooooooooooooooooooooooooooooooooong,
    Loooooooooooooooooooong,
    Looooooooooooong,
]: ...


# long function name, no param list, no return value
def thiiiiiiiiiiiiiiiiiis_iiiiiiiiiiiiiiiiiiiiiiiiiiiiiis_veeeeeeeeeeeeeeeeeeeeeeery_looooooong():
    pass


# long function name, no param list
def thiiiiiiiiiiiiiiiiiis_iiiiiiiiiiiiiiiiiiiiiiiiiiiiiis_veeeeeeeeeeeeeeeeeeeeeeery_looooooong() -> (
    list[int, float]
): ...


# long function name, no return value
def thiiiiiiiiiiiiiiiiiis_iiiiiiiiiiiiiiiiiiiiiiiiiiiiiis_veeeeeeeeeeeeeeeeeeeeeeery_looooooong(
    a, b
): ...


# unskippable type hint (??)
def foo(a) -> list[aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa]:  # type: ignore
    pass


def foo(
    a,
) -> list[
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
]:  # abpedeifnore
    pass


def foo(
    a,
    b: list[Bad],
): ...  # type: ignore


# don't lose any comments (no magic)
def foo(a, b) -> list[a, b]:  # 1  # 2  # 3  # 4  # 5
    ...  # 6


# don't lose any comments (param list magic)
def foo(  # 1
    a,  # 2
    b,
) -> list[a, b]:  # 3  # 4  # 5
    ...  # 6


# don't lose any comments (return type magic)
def foo(a, b) -> list[  # 1  # 2  # 3
    a,  # 4
    b,
]:  # 5
    ...  # 6


# don't lose any comments (both magic)
def foo(  # 1
    a,  # 2
    b,
) -> list[  # 3
    a,  # 4
    b,
]:  # 5
    ...  # 6


# real life example
def SimplePyFn(
    context: hl.GeneratorContext,
    buffer_input: Buffer[UInt8, 2],
    func_input: Buffer[Int32, 2],
    float_arg: Scalar[Float32],
    offset: int = 0,
) -> tuple[
    Buffer[UInt8, 2],
    Buffer[UInt8, 2],
]: ...
