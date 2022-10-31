first_item, second_item = (
    some_looooooooong_module.some_looooooooooooooong_function_name(
        first_argument, second_argument, third_argument
    )
)

some_dict["with_a_long_key"] = (
    some_looooooooong_module.some_looooooooooooooong_function_name(
        first_argument, second_argument, third_argument
    )
)

# Make sure it works when the RHS only has one pair of (optional) parens.
first_item, second_item = (
    some_looooooooong_module.SomeClass.some_looooooooooooooong_variable_name
)

some_dict["with_a_long_key"] = (
    some_looooooooong_module.SomeClass.some_looooooooooooooong_variable_name
)

# Make sure chaining assignments work.
first_item, second_item, third_item, forth_item = m["everything"] = (
    some_looooooooong_module.some_looooooooooooooong_function_name(
        first_argument, second_argument, third_argument
    )
)

# Make sure when the RHS's first split at the non-optional paren fits,
# we split there instead of the outer RHS optional paren.
first_item, second_item = some_looooooooong_module.some_loooooog_function_name(
    first_argument, second_argument, third_argument
)

(
    first_item,
    second_item,
    third_item,
    forth_item,
    fifth_item,
    last_item_very_loooooong,
) = some_looooooooong_module.some_looooooooooooooong_function_name(
    first_argument, second_argument, third_argument
)

(
    first_item,
    second_item,
    third_item,
    forth_item,
    fifth_item,
    last_item_very_loooooong,
) = everyting = some_loooooog_function_name(
    first_argument, second_argument, third_argument
)
