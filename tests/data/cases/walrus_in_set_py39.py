# flags: --minimum-version=3.9 --target-version=py39
# Python 3.9.0 can't parse a named expression in a set literal without
# parentheses, so they're kept for 3.9 targets.
x = {(y := 1)}
x = {((y := 1))}
x = [(y := 1)]


def seen_ids(rows):
    return {(first := rows[0].id)}, first

# output
# Python 3.9.0 can't parse a named expression in a set literal without
# parentheses, so they're kept for 3.9 targets.
x = {(y := 1)}
x = {(y := 1)}
x = [y := 1]


def seen_ids(rows):
    return {(first := rows[0].id)}, first
