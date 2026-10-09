# flags: --minimum-version=3.9 --target-version=py39
# Since Python 3.9, the parentheses around a named expression in a set literal
# can be removed.
x = {(y := 1)}
x = {((y := 1))}
x = [(y := 1)]


def seen_ids(rows):
    return {(first := rows[0].id)}, first

# output
# Since Python 3.9, the parentheses around a named expression in a set literal
# can be removed.
x = {y := 1}
x = {y := 1}
x = [y := 1]


def seen_ids(rows):
    return {first := rows[0].id}, first
