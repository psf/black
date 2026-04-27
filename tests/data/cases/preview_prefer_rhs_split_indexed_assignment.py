# flags: --preview

# Indexed assignment with a short RHS expression should not get unnecessary parens.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = 10 - 5

# Unformatted input: the unnecessary parens should be removed.
dictionary_of_arrays["long_key_name_for_the_example"][very_long_index_name, index_zero] = (10 - 5)

# Longer RHS expressions that fit on the tail line should also lose parens.
dictionary_of_arrays["long_key_name_for_the_example"][very_long_index_name, index_zero] = (1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1)

# RHS with brackets (function call) should also lose unnecessary parens.
dictionary_of_arrays["long_key_name_for_the_example"][very_long_index_name, index_zero] = (some_function(arg1, arg2))

# output

# Indexed assignment with a short RHS expression should not get unnecessary parens.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = 10 - 5

# Unformatted input: the unnecessary parens should be removed.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = 10 - 5

# Longer RHS expressions that fit on the tail line should also lose parens.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1

# RHS with brackets (function call) should also lose unnecessary parens.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = some_function(arg1, arg2)
