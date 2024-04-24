# flags: --minimum-version=3.13

type A[T=int] = float
type B[*P=int] = float
type C[*Ts=int] = float
type D[*Ts=*int] = float

# output

type A[T = int] = float
type B[*P = int] = float
type C[*Ts = int] = float
type D[*Ts = *int] = float
