# `# fmt: skip` after the closing bracket of a multi-line call or subscript that
# isn't the last element in brackets. Only that element is left alone.
x = {
    "a":  1,
    "b": f(
        a  ,  b
    ),  # fmt: skip
    "c":  [1,2],
}

y = [
    a,
    obj.method(
        a  ,  b
    ).other(  c  ),  # fmt: skip
    d  +  e,
]

z = [
    a  +  b[
        c
    ],  # fmt: skip
    d,
]

result = f(
    a,
    g(
        b  ,  c
    ),  # fmt: skip
    d  +  e,
)

# output
# `# fmt: skip` after the closing bracket of a multi-line call or subscript that
# isn't the last element in brackets. Only that element is left alone.
x = {
    "a": 1,
    "b": f(
        a  ,  b
    ),  # fmt: skip
    "c": [1, 2],
}

y = [
    a,
    obj.method(
        a  ,  b
    ).other(  c  ),  # fmt: skip
    d + e,
]

z = [
    a  +  b[
        c
    ],  # fmt: skip
    d,
]

result = f(
    a,
    g(
        b  ,  c
    ),  # fmt: skip
    d + e,
)
