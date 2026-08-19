# Parentheses around the target of an annotated assignment are load bearing:
# `(x): int = 5` leaves `x` out of `__annotations__`, while `x: int = 5` puts it
# there. Removing them changes what the module does at runtime.
(x): int = 5
(y): int

# One pair is what makes the target non-simple, so the nesting above it is
# redundant and gets removed.
((z)): int = 5
(((q))): int = 5


class C:
    (attr): int = 5


def f():
    (local): int = 5


# Attribute and subscript targets are non-simple with or without the parentheses,
# so those are still stripped.
(obj.attr): int = 5
(obj[0]): int = 5

# And a plain assignment carries no annotation, so its parentheses go too.
(w) = 5

# output

# Parentheses around the target of an annotated assignment are load bearing:
# `(x): int = 5` leaves `x` out of `__annotations__`, while `x: int = 5` puts it
# there. Removing them changes what the module does at runtime.
(x): int = 5
(y): int

# One pair is what makes the target non-simple, so the nesting above it is
# redundant and gets removed.
(z): int = 5
(q): int = 5


class C:
    (attr): int = 5


def f():
    (local): int = 5


# Attribute and subscript targets are non-simple with or without the parentheses,
# so those are still stripped.
obj.attr: int = 5
obj[0]: int = 5

# And a plain assignment carries no annotation, so its parentheses go too.
w = 5
