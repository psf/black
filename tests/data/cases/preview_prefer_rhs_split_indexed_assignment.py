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

# A long RHS that does not fit on the tail line still gets wrapped in parens.
dictionary_of_arrays["long_key_name_for_the_example"][very_long_index_name, index_zero] = (aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa + bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb)

# Regression: a ternary RHS with a short target must keep its parentheses
# (no splitting inside the function call).
kwargs["empty_label"] = (
    kwargs.get("empty_label", _("None")) if db_field.blank else None_None_None
)

# Regression: a method-chain RHS with a short target must keep its parentheses.
two_factor_form["totp_value"] = (
    _get_totp(user.totp_secret).generate(time.time()).decode()
)

# Regression: parenthesized tuple targets are not indexed assignments.
(self.next,) = (
    self._unpack("Q", self._ensure_read(fp, 8))
    if self._bigtiff
    else self._unpack("L", self._ensure_read(fp, 4))
)

# Regression: the `]` of an annotation is not a subscripted target.
self.args: list[str] = (
    args[1:] if self.ignore_exit_code or self.invert_exit_code else args_args_args
)

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

# A long RHS that does not fit on the tail line still gets wrapped in parens.
dictionary_of_arrays["long_key_name_for_the_example"][
    very_long_index_name, index_zero
] = (
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    + bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
)

# Regression: a ternary RHS with a short target must keep its parentheses
# (no splitting inside the function call).
kwargs["empty_label"] = (
    kwargs.get("empty_label", _("None")) if db_field.blank else None_None_None
)

# Regression: a method-chain RHS with a short target must keep its parentheses.
two_factor_form["totp_value"] = (
    _get_totp(user.totp_secret).generate(time.time()).decode()
)

# Regression: parenthesized tuple targets are not indexed assignments.
(self.next,) = (
    self._unpack("Q", self._ensure_read(fp, 8))
    if self._bigtiff
    else self._unpack("L", self._ensure_read(fp, 4))
)

# Regression: the `]` of an annotation is not a subscripted target.
self.args: list[str] = (
    args[1:] if self.ignore_exit_code or self.invert_exit_code else args_args_args
)
