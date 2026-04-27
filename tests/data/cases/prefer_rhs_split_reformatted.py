# Test cases separate from `prefer_rhs_split.py` that contains unformatted source.

# Left hand side fits in a single line but will still be exploded by the
# magic trailing comma.
first_value, (m1, m2,), third_value = xxxxxx_yyyyyy_zzzzzz_wwwwww_uuuuuuu_vvvvvvvvvvv(
    arg1,
    arg2,
)

# Make when when the left side of assignment plus the opening paren "... = (" is
# exactly line length limit + 1, it won't be split like that.
xxxxxxxxx_yyy_zzzzzzzz[xx.xxxxxx(x_yyy_zzzzzz.xxxxx[0]), x_yyy_zzzzzz.xxxxxx(xxxx=1)] = 1

# Regression test for #1187
print(
    dict(
        a=1,
        b=2 if some_kind_of_data is not None else some_other_kind_of_data,  # some explanation of why this is actually necessary
        c=3,
    )
)

# Regression: subscript access chain on RHS should not be split mid-chain
some_node.children[1].prefix = some_node.children[0].prefix + some_node.children[1].prefix

another_node.children[idx].value = another_node.children[idx - 1].value + another_node.children[idx + 1].value

# output


# Test cases separate from `prefer_rhs_split.py` that contains unformatted source.

# Left hand side fits in a single line but will still be exploded by the
# magic trailing comma.
(
    first_value,
    (
        m1,
        m2,
    ),
    third_value,
) = xxxxxx_yyyyyy_zzzzzz_wwwwww_uuuuuuu_vvvvvvvvvvv(
    arg1,
    arg2,
)

# Make when when the left side of assignment plus the opening paren "... = (" is
# exactly line length limit + 1, it won't be split like that.
xxxxxxxxx_yyy_zzzzzzzz[
    xx.xxxxxx(x_yyy_zzzzzz.xxxxx[0]), x_yyy_zzzzzz.xxxxxx(xxxx=1)
] = 1

# Regression test for #1187
print(
    dict(
        a=1,
        b=(
            2 if some_kind_of_data is not None else some_other_kind_of_data
        ),  # some explanation of why this is actually necessary
        c=3,
    )
)

# Regression: subscript access chain on RHS should not be split mid-chain
some_node.children[1].prefix = (
    some_node.children[0].prefix + some_node.children[1].prefix
)

another_node.children[idx].value = (
    another_node.children[idx - 1].value + another_node.children[idx + 1].value
)
