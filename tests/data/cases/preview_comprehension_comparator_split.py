# flags: --preview --line-length=88

# Regression test for https://github.com/psf/black/issues/4514
# Black used to split between the variable and the comparator (`if t / not in`)
# when the RHS was a bracketed expression that had to break: either via a
# magic trailing comma or because the line was too long. With the fix, the
# bracket explodes and the comparator stays put.

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

# Same shape without a magic trailing comma: the RHS bracket is long enough
# that Black has to break it anyway. The comparator should stay with `if t`.
no_magic_not_in = [
    t
    for t in y
    if t not in some_very_long_function_name(argument_one, argument_two, argument_three, argument_four)
]

no_magic_equality = [
    t
    for t in y
    if t == some_very_long_function_name(argument_one, argument_two, argument_three, argument_four)
]

no_magic_less_than = [
    t
    for t in y
    if t < some_very_long_function_name(argument_one, argument_two, argument_three, argument_four)
]

no_magic_identity = [
    t
    for t in y
    if t is some_very_long_function_name(argument_one, argument_two, argument_three, argument_four)
]

# output

# Regression test for https://github.com/psf/black/issues/4514
# Black used to split between the variable and the comparator (`if t / not in`)
# when the RHS was a bracketed expression that had to break: either via a
# magic trailing comma or because the line was too long. With the fix, the
# bracket explodes and the comparator stays put.

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

# Same shape without a magic trailing comma: the RHS bracket is long enough
# that Black has to break it anyway. The comparator should stay with `if t`.
no_magic_not_in = [
    t
    for t in y
    if t not in some_very_long_function_name(
        argument_one, argument_two, argument_three, argument_four
    )
]

no_magic_equality = [
    t
    for t in y
    if t == some_very_long_function_name(
        argument_one, argument_two, argument_three, argument_four
    )
]

no_magic_less_than = [
    t
    for t in y
    if t < some_very_long_function_name(
        argument_one, argument_two, argument_three, argument_four
    )
]

no_magic_identity = [
    t
    for t in y
    if t is some_very_long_function_name(
        argument_one, argument_two, argument_three, argument_four
    )
]
