# flags: --line-ranges=26-26
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The statements outside of the range contain a `# fmt: skip` on a line of their own
# inside brackets, followed by the closing bracket. They are kept as they are.
x = (
    a  +  b,  # fmt: skip
    (c),
)

y = foo(
    1  +  2  # fmt: skip
)

if (
    cond  # fmt: skip
):
    pass

for item in [
    1,  # fmt: skip
]:
    pass

z   =   1

w = {
    "key":  value  # fmt: skip
}

# output

# flags: --line-ranges=26-26
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The statements outside of the range contain a `# fmt: skip` on a line of their own
# inside brackets, followed by the closing bracket. They are kept as they are.
x = (
    a  +  b,  # fmt: skip
    (c),
)

y = foo(
    1  +  2  # fmt: skip
)

if (
    cond  # fmt: skip
):
    pass

for item in [
    1,  # fmt: skip
]:
    pass

z = 1

w = {
    "key":  value  # fmt: skip
}
