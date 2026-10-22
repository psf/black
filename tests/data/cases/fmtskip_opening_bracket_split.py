# `# fmt: skip` on an opening bracket that is followed by more code on the
# closing bracket's line. The hidden code ends in code, not in a comment, so the
# rest of the line must stay on the same line instead of being split off.

x = [  # fmt: skip
    1, 2] + [3]

y = {  # fmt: skip
    "a": 1} | {"b": 2}

z = (  # fmt: skip
    1) + 2

w = [  # fmt: skip
    1, 2].copy()

if [  # fmt: skip
    1] == [2]:
    pass


def f():
    return [  # fmt: skip
        1] + [2]

# output

# `# fmt: skip` on an opening bracket that is followed by more code on the
# closing bracket's line. The hidden code ends in code, not in a comment, so the
# rest of the line must stay on the same line instead of being split off.

x = [  # fmt: skip
    1, 2] + [
    3
]

y = {  # fmt: skip
    "a": 1} | {
    "b": 2
}

z = (  # fmt: skip
    1) + 2

w = [  # fmt: skip
    1, 2].copy()

if [  # fmt: skip
    1] == [
    2
]:
    pass


def f():
    return [  # fmt: skip
        1] + [
        2
    ]
