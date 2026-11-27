# flags: --minimum-version=3.12
# Inside brackets, a line holding only a backslash can also follow a blank line
# or a comment. Code written back as is must keep it.

# fmt: off
x = [1,

     \
     2]
y = [1,
     # comment
     \
     2]
# fmt: on

w = [1,
     # comment
     \
     2]  # fmt: skip

z = f"""{value =
# comment
\
}"""

a = [
    1,
    # comment
    \
    2,
]

# output
# Inside brackets, a line holding only a backslash can also follow a blank line
# or a comment. Code written back as is must keep it.

# fmt: off
x = [1,

     \
     2]
y = [1,
     # comment
     \
     2]
# fmt: on

w = [1,
     # comment
     \
     2]  # fmt: skip

z = f"""{value =
# comment
\
}"""

a = [
    1,
    # comment
    2,
]
