# flags: --minimum-version=3.10 --target-version=py310
# Since Python 3.10, the parentheses around a named expression in a set literal
# can be removed.
x = {(y := 1)}
x = {((y := 1))}
x = [(y := 1)]


def seen_ids(rows):
    return {(first := rows[0].id)}, first

# output
# Since Python 3.10, the parentheses around a named expression in a set literal
# can be removed.
x = {y := 1}
x = {y := 1}
x = [y := 1]


def seen_ids(rows):
    return {first := rows[0].id}, first
