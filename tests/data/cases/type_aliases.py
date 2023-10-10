# flags: --minimum-version=3.12
type A=int
type Gen[T]=list[T]

type = aliased
print(type(42))

# output

type A = int
type Gen[T] = list[T]

type = aliased
print(type(42))
