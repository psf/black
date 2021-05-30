aaa = my_function(
    foo="test, this is a sample value",
    bar=some_long_value_name_foo_bar_baz
    if some_boolean_variable
    else some_fallback_value_foo_bar_baz,
    baz="hello, this is a another value",
)

# output

aaa = my_function(
    foo="test, this is a sample value",
    bar=(
        some_long_value_name_foo_bar_baz
        if some_boolean_variable
        else some_fallback_value_foo_bar_baz
    ),
    baz="hello, this is a another value",
)
