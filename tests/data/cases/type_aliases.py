# flags: --minimum-version=3.12

type A=int
type Gen[T]=list[T]
type Alias[T]=lambda: T
type And[T]=T and T
type IfElse[T]=T if T else T
type One = int; type Another = str
class X: type InClass = int

type = aliased
print(type(42))

# output

type A = int
type Gen[T] = list[T]
type Alias[T] = lambda: T
type And[T] = T and T
type IfElse[T] = T if T else T
type One = int
type Another = str


class X:
    type InClass = int


type = aliased
print(type(42))
