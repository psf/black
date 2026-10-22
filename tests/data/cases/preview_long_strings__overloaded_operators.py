# flags: --unstable --line-length=20
x += "directory subdirectory file.txt"
variable += "foo bar"
x -= "directory subdirectory file.txt"
variable -= "foo bar"
x *= "directory subdirectory file.txt"
variable *= "foo bar"
x @= "directory subdirectory file.txt"
variable @= "foo bar"
x /= "directory subdirectory file.txt"
variable /= "foo bar"
x //= "directory subdirectory file.txt"
variable //= "foo bar"
x %= "directory subdirectory file.txt"
variable %= "foo bar"
x **= "directory subdirectory file.txt"
variable **= "foo bar"
x <<= "directory subdirectory file.txt"
variable <<= "foo bar"
x >>= "directory subdirectory file.txt"
variable >>= "foo bar"
x &= "directory subdirectory file.txt"
variable &= "foo bar"
x |= "directory subdirectory file.txt"
variable |= "foo bar"
x ^= "directory subdirectory file.txt"
variable ^= "foo bar"
x + "directory subdirectory file.txt"
x - "directory subdirectory file.txt"
x * "directory subdirectory file.txt"
x @ "directory subdirectory file.txt"
x / "directory subdirectory file.txt"
x // "directory subdirectory file.txt"
x % "directory subdirectory file.txt"
x ** "directory subdirectory file.txt"
x << "directory subdirectory file.txt"
x >> "directory subdirectory file.txt"
x & "directory subdirectory file.txt"
x | "directory subdirectory file.txt"
x ^ "directory subdirectory file.txt"
x * "directory subdirectory file.txt" % y
x @ "directory subdirectory file.txt" % y
x / "directory subdirectory file.txt" % y
x // "directory subdirectory file.txt" % y
x % "directory subdirectory file.txt" % y
x ** "directory subdirectory file.txt" % y

# output

x += (
    "directory"
    " subdirectory"
    " file.txt"
)
variable += (
    "foo bar"
)
x -= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable -= (
    "foo bar"
)
x *= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable *= (
    "foo bar"
)
x @= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable @= (
    "foo bar"
)
x /= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable /= (
    "foo bar"
)
x //= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable //= (
    "foo bar"
)
x %= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable %= (
    "foo bar"
)
x **= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable **= (
    "foo bar"
)
x <<= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable <<= (
    "foo bar"
)
x >>= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable >>= (
    "foo bar"
)
x &= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable &= (
    "foo bar"
)
x |= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable |= (
    "foo bar"
)
x ^= (
    "directory"
    " subdirectory"
    " file.txt"
)
variable ^= (
    "foo bar"
)
x + (
    "directory"
    " subdirectory"
    " file.txt"
)
x - (
    "directory"
    " subdirectory"
    " file.txt"
)
x * (
    "directory"
    " subdirectory"
    " file.txt"
)
x @ (
    "directory"
    " subdirectory"
    " file.txt"
)
x / (
    "directory"
    " subdirectory"
    " file.txt"
)
x // (
    "directory"
    " subdirectory"
    " file.txt"
)
x % (
    "directory"
    " subdirectory"
    " file.txt"
)
x ** (
    "directory"
    " subdirectory"
    " file.txt"
)
x << (
    "directory"
    " subdirectory"
    " file.txt"
)
x >> (
    "directory"
    " subdirectory"
    " file.txt"
)
x & (
    "directory"
    " subdirectory"
    " file.txt"
)
x | (
    "directory"
    " subdirectory"
    " file.txt"
)
x ^ (
    "directory"
    " subdirectory"
    " file.txt"
)
x * "directory subdirectory file.txt" % y
x @ "directory subdirectory file.txt" % y
x / "directory subdirectory file.txt" % y
x // "directory subdirectory file.txt" % y
x % "directory subdirectory file.txt" % y
x ** "directory subdirectory file.txt" % y
