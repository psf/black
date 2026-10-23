# `# fmt: skip` on an opening bracket can hide the start of a conditional
# expression. The rest of the expression stays after the closing bracket.

x = (  # fmt: skip
    a
) if condition else b

y = [  # fmt: skip
    1, 2] if condition else []

z = a if (  # fmt: skip
    b
) else c

f = lambda: (  # fmt: skip
    a
) if condition else b

while (  # fmt: skip
    a
) if condition else b:
    x  =  1


def f():
    return (  # fmt: skip
        a
    ) if condition else b

# output

# `# fmt: skip` on an opening bracket can hide the start of a conditional
# expression. The rest of the expression stays after the closing bracket.

x = (  # fmt: skip
    a
) if condition else b

y = [  # fmt: skip
    1, 2] if condition else []

z = a if (  # fmt: skip
    b
) else c

f = lambda: (  # fmt: skip
    a
) if condition else b

while (  # fmt: skip
    a
) if condition else b:
    x = 1


def f():
    return (  # fmt: skip
        a
    ) if condition else b
