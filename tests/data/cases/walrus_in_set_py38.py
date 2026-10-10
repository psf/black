# flags: --minimum-version=3.8
# Python 3.8 needs the parentheses around a named expression in a set literal.
x = {(y := 1)}
x = {((y := 1))}
x = {(  # comment
    y := 1
)}
x = [(y := 1)]
x = {(y := 1), 2}
x = {(y := f(z)) for z in w}


def seen_ids(rows):
    return {(first := rows[0].id)}, first

# output
# Python 3.8 needs the parentheses around a named expression in a set literal.
x = {(y := 1)}
x = {(y := 1)}
x = {(y := 1)}  # comment
x = [y := 1]
x = {(y := 1), 2}
x = {(y := f(z)) for z in w}


def seen_ids(rows):
    return {(first := rows[0].id)}, first
