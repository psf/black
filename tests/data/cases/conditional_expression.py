# flags: --preview
long_kwargs_single_line = my_function(
    foo="test, this is a sample value",
    bar=some_long_value_name_foo_bar_baz if some_boolean_variable else some_fallback_value_foo_bar_baz,
    baz="hello, this is a another value",
)

multiline_kwargs_indented = my_function(
    foo="test, this is a sample value",
    bar=some_long_value_name_foo_bar_baz
    if some_boolean_variable
    else some_fallback_value_foo_bar_baz,
    baz="hello, this is a another value",
)

imploding_kwargs = my_function(
    foo="test, this is a sample value",
    bar=a
    if foo
    else b,
    baz="hello, this is a another value",
)

imploding_line = (
    1
    if 1 + 1 == 2
    else 0
)

exploding_line = "hello this is a slightly long string" if some_long_value_name_foo_bar_baz else "this one is a little shorter"

positional_argument_test(some_long_value_name_foo_bar_baz if some_boolean_variable else some_fallback_value_foo_bar_baz)

def weird_default_argument(x=some_long_value_name_foo_bar_baz
        if SOME_CONSTANT
        else some_fallback_value_foo_bar_baz):
    pass

nested = "hello this is a slightly long string" if (some_long_value_name_foo_bar_baz if
                                                    nesting_test_expressions else some_fallback_value_foo_bar_baz) \
    else "this one is a little shorter"

generator_expression = (
    some_long_value_name_foo_bar_baz if some_boolean_variable else some_fallback_value_foo_bar_baz for some_boolean_variable in some_iterable
)


def limit_offset_sql(self, low_mark, high_mark):
    """Return LIMIT/OFFSET SQL clause."""
    limit, offset = self._get_limit_offset_params(low_mark, high_mark)
    return " ".join(
        sql
        for sql in (
            "LIMIT %d" % limit if limit else None,
            ("OFFSET %d" % offset) if offset else None,
        )
        if sql
    )


def something():
    clone._iterable_class = (
        NamedValuesListIterable
        if named
        else FlatValuesListIterable
        if flat
        else ValuesListIterable
    )

# output

long_kwargs_single_line = my_function(
    foo="test, this is a sample value",
    bar=(
        some_long_value_name_foo_bar_baz
        if some_boolean_variable
        else some_fallback_value_foo_bar_baz
    ),
    baz="hello, this is a another value",
)

multiline_kwargs_indented = my_function(
    foo="test, this is a sample value",
    bar=(
        some_long_value_name_foo_bar_baz
        if some_boolean_variable
        else some_fallback_value_foo_bar_baz
    ),
    baz="hello, this is a another value",
)

imploding_kwargs = my_function(
    foo="test, this is a sample value",
    bar=a if foo else b,
    baz="hello, this is a another value",
)

imploding_line = 1 if 1 + 1 == 2 else 0

exploding_line = (
    "hello this is a slightly long string"
    if some_long_value_name_foo_bar_baz
    else "this one is a little shorter"
)

positional_argument_test(
    some_long_value_name_foo_bar_baz
    if some_boolean_variable
    else some_fallback_value_foo_bar_baz
)


def weird_default_argument(
    x=(
        some_long_value_name_foo_bar_baz
        if SOME_CONSTANT
        else some_fallback_value_foo_bar_baz
    ),
):
    pass


nested = (
    "hello this is a slightly long string"
    if (
        some_long_value_name_foo_bar_baz
        if nesting_test_expressions
        else some_fallback_value_foo_bar_baz
    )
    else "this one is a little shorter"
)

generator_expression = (
    (
        some_long_value_name_foo_bar_baz
        if some_boolean_variable
        else some_fallback_value_foo_bar_baz
    )
    for some_boolean_variable in some_iterable
)


def limit_offset_sql(self, low_mark, high_mark):
    """Return LIMIT/OFFSET SQL clause."""
    limit, offset = self._get_limit_offset_params(low_mark, high_mark)
    return " ".join(
        sql
        for sql in (
            "LIMIT %d" % limit if limit else None,
            ("OFFSET %d" % offset) if offset else None,
        )
        if sql
    )


def something():
    clone._iterable_class = (
        NamedValuesListIterable
        if named
        else FlatValuesListIterable if flat else ValuesListIterable
    )
