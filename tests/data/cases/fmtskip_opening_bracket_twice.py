# Two `# fmt: skip` comments on opening brackets in the same statement. The
# second hidden part starts on the line where the first one ends, so it has to
# stay there.

x = a if (  # fmt: skip
    b
) else (  # fmt: skip
    c
)

y = (  # fmt: skip
    a
) if (  # fmt: skip
    b
) else c

z = (  # fmt: skip
    a
) if (  # fmt: skip
    b
) else (  # fmt: skip
    c
)

w = (  # fmt: skip
    a
) + (  # fmt: skip
    b
)

if (  # fmt: skip
    a
) if (  # fmt: skip
    b
) else c:
    x  =  1


def f():
    return (  # fmt: skip
        a
    ) if (  # fmt: skip
        b
    ) else c

# output

# Two `# fmt: skip` comments on opening brackets in the same statement. The
# second hidden part starts on the line where the first one ends, so it has to
# stay there.

x = a if (  # fmt: skip
    b
) else (  # fmt: skip
    c
)

y = (  # fmt: skip
    a
) if (  # fmt: skip
    b
) else c

z = (  # fmt: skip
    a
) if (  # fmt: skip
    b
) else (  # fmt: skip
    c
)

w = (  # fmt: skip
    a
) + (  # fmt: skip
    b
)

if (  # fmt: skip
    a
) if (  # fmt: skip
    b
) else c:
    x = 1


def f():
    return (  # fmt: skip
        a
    ) if (  # fmt: skip
        b
    ) else c
