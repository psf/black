# flags: --preview --target-version=py38
# Python 3.9 and older need the parentheses around a named expression in a
# subscript.
x[(y := 1)]
x[((y := 1))]
x[(  # comment
    y := 1
)]
x[(y := 1)] = z
x[(1)]


def lookup(keys, values, key):
    return values[(i := bisect_left(keys, key))], i

# output
# Python 3.9 and older need the parentheses around a named expression in a
# subscript.
x[(y := 1)]
x[(y := 1)]
x[(y := 1)]  # comment
x[(y := 1)] = z
x[1]


def lookup(keys, values, key):
    return values[(i := bisect_left(keys, key))], i
