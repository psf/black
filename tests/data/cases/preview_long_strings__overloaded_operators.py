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
x * "short" * "directory subdirectory file.txt" % y
x * "directory subdirectory file.txt" % "directory subdirectory file.txt"
x ** "directory subdirectory file.txt" ** y
x * "directory subdirectory file.txt".replace("file", "dir") % y
f(x * "directory subdirectory file.txt" % y)
x * ("directory subdirectory file.txt") % y
x * "directory subdirectory file.txt" % y  # keep this

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
x * (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x @ (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x / (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x // (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x % (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x ** (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x * "short" * (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x * (
    "directory"
    " subdirectory"
    " file.txt"
) % (
    "directory"
    " subdirectory"
    " file.txt"
)
x ** (
    "directory"
    " subdirectory"
    " file.txt"
) ** y
x * (
    "directory"
    " subdirectory"
    " file.txt"
    .replace(
        "file",
        "dir",
    )
) % y
f(
    x
    * "directory"
    " subdirectory"
    " file.txt"
    % y
)
x * (
    "directory"
    " subdirectory"
    " file.txt"
) % y
x * (
    "directory"
    " subdirectory"
    " file.txt"
) % y  # keep this
