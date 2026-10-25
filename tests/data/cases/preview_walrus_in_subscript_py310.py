# flags: --preview --target-version=py310
# Since Python 3.10, the parentheses around a named expression in a subscript
# can be removed.
x[(y := 1)]
x[((y := 1))]
x[(y := 1)] = z
x[(1)]


def lookup(keys, values, key):
    return values[(i := bisect_left(keys, key))], i

# output
# Since Python 3.10, the parentheses around a named expression in a subscript
# can be removed.
x[y := 1]
x[y := 1]
x[y := 1] = z
x[1]


def lookup(keys, values, key):
    return values[i := bisect_left(keys, key)], i
