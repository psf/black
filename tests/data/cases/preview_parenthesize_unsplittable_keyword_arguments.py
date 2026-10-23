# flags: --preview
# Regression test for https://github.com/psf/black/issues/2893

# An unsplittable attribute-chain value now wraps in parentheses.
some_result = some_function(
    long_long_long_long_long_long_long_long_long_long_long_arg=
    long_long_long_long_long_class.long_long_long_long_attr
)

# Values that already have a split point are unaffected: the binop still splits
# at the operator and the subscript still splits at the brackets.
another_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=first_value + second_value,
    long_long_long_long_long_long_long_long_long_long_long_other=some_dict["key"],
)

# A name so long that `name=(` would still exceed the limit is left alone.
normal_name = normal_function_name(
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)

# output

# Regression test for https://github.com/psf/black/issues/2893

# An unsplittable attribute-chain value now wraps in parentheses.
some_result = some_function(
    long_long_long_long_long_long_long_long_long_long_long_arg=(
        long_long_long_long_long_class.long_long_long_long_attr
    )
)

# Values that already have a split point are unaffected: the binop still splits
# at the operator and the subscript still splits at the brackets.
another_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=first_value
    + second_value,
    long_long_long_long_long_long_long_long_long_long_long_other=some_dict["key"],
)

# A name so long that `name=(` would still exceed the limit is left alone.
normal_name = normal_function_name(
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)
