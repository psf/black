# flags: --unstable --line-length=20
x /= "directory subdirectory file.txt"
x / "directory subdirectory file.txt"
variable @= "foo bar"

# output

x /= (
    "directory"
    " subdirectory"
    " file.txt"
)
x / (
    "directory"
    " subdirectory"
    " file.txt"
)
variable @= (
    "foo bar"
)
