# A statement hidden by `# fmt: skip` takes its newline with it, so a hidden
# statement right after it must still start on a new line.

foo(a  # fmt: skip
)
bar(b  # fmt: skip
)

x = [1  # fmt: skip
]
y = [2  # fmt: skip
]

x = (  # fmt: skip
    a
)
with (  # fmt: skip
    b
):
    x  =  1

if foo(a  # fmt: skip
):
    pass
if (  # fmt: skip
    a
):
    pass

foo(a  # fmt: skip
)
class A(  # fmt: skip
    b
): pass

foo(a  # fmt: skip
)
@dec(b  # fmt: skip
)
def f(): pass


def f():
    foo(a  # fmt: skip
    )
    return (b  # fmt: skip
    )

# output

# A statement hidden by `# fmt: skip` takes its newline with it, so a hidden
# statement right after it must still start on a new line.

foo(a  # fmt: skip
)
bar(b  # fmt: skip
)

x = [1  # fmt: skip
]
y = [2  # fmt: skip
]

x = (  # fmt: skip
    a
)
with (  # fmt: skip
    b
):
    x = 1

if foo(a  # fmt: skip
):
    pass
if (  # fmt: skip
    a
):
    pass

foo(a  # fmt: skip
)
class A(  # fmt: skip
    b
): pass

foo(a  # fmt: skip
)
@dec(b  # fmt: skip
)
def f(): pass


def f():
    foo(a  # fmt: skip
    )
    return (b  # fmt: skip
    )
