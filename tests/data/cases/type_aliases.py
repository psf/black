# flags: --minimum-version=3.12
type A=int
type Gen[T]=list[T]
type One = int; type Another = str
class X: type InClass = int

type = aliased
print(type(42))

# output

type A = int
type Gen[T] = list[T]
type One = int
type Another = str


class X:
    type InClass = int


type = aliased
print(type(42))
