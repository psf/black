# flags: --preview

# Indexed assignment with a short RHS expression should not get unnecessary parens.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = 10 - 5

# Unformatted input: the unnecessary parens should be removed.
dictionary_of_arrays["long_key_name_for_the_example"][very_long_index_name, index_zero] = (10 - 5)

# output

# Indexed assignment with a short RHS expression should not get unnecessary parens.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = 10 - 5

# Unformatted input: the unnecessary parens should be removed.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = 10 - 5
