# flags: --preview --line-length=88

# Regression test for https://github.com/psf/black/issues/4514
# Black used to split between the variable and the comparator (`if t / not in`)
# when the RHS was a bracketed expression with a magic trailing comma. With the
# fix, the bracket explodes via right_hand_split and the comparator stays put.

x = [
    t
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]

gen = (
    t
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
)

s = {
    t
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
}

d = {
    t: True
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
}

equality = [
    t
    for t in y
    if t == {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]

membership = [
    t
    for t in y
    if t in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]

less_than = [
    t
    for t in y
    if t < SomeFunction(
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    )
]

identity = [
    t
    for t in y
    if t is SomeClass(
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    )
]

# A logical operator combined with a comparator: the `or` splits first, and the
# remaining `a in {...,}` then defers to the bracket split instead of splitting
# at `in`.
combined = [
    t
    for t in y
    if some_short_predicate
    or t in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]

# output

# Regression test for https://github.com/psf/black/issues/4514
# Black used to split between the variable and the comparator (`if t / not in`)
# when the RHS was a bracketed expression with a magic trailing comma. With the
# fix, the bracket explodes via right_hand_split and the comparator stays put.

x = [
    t
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]

gen = (
    t
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
)

s = {
    t
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
}

d = {
    t: True
    for t in y
    if t not in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
}

equality = [
    t
    for t in y
    if t == {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]

membership = [
    t
    for t in y
    if t in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]

less_than = [
    t
    for t in y
    if t < SomeFunction(
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    )
]

identity = [
    t
    for t in y
    if t is SomeClass(
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    )
]

# A logical operator combined with a comparator: the `or` splits first, and the
# remaining `a in {...,}` then defers to the bracket split instead of splitting
# at `in`.
combined = [
    t
    for t in y
    if some_short_predicate
    or t in {
        LongNameOne,
        LongNameTwo,
        LongNameThree,
    }
]
