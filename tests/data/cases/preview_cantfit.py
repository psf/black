# flags: --preview
# long variable name
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = 0
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = 1  # with a comment
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = [
    1, 2, 3
]
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = function()
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = function(
    arg1, arg2, arg3
)
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = function(
    [1, 2, 3], arg1, [1, 2, 3], arg2, [1, 2, 3], arg3
)
# long function name
normal_name = but_the_function_name_is_now_ridiculously_long_and_it_is_still_super_annoying()
normal_name = but_the_function_name_is_now_ridiculously_long_and_it_is_still_super_annoying(
    arg1, arg2, arg3
)
normal_name = but_the_function_name_is_now_ridiculously_long_and_it_is_still_super_annoying(
    [1, 2, 3], arg1, [1, 2, 3], arg2, [1, 2, 3], arg3
)
# long arguments
normal_name = normal_function_name(
    "but with super long string arguments that on their own exceed the line limit so there's no way it can ever fit",
    "eggs with spam and eggs and spam with eggs with spam and eggs and spam with eggs with spam and eggs and spam with eggs",
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)
string_variable_name = (
    "a string that is waaaaaaaayyyyyyyy too long, even in parens, there's nothing you can do"  # noqa
)
for key in """
    hostname
    port
    username
""".split():
    if key in self.connect_kwargs:
        raise ValueError(err.format(key))
concatenated_strings = "some strings that are " "concatenated implicitly, so if you put them on separate " "lines it will fit"
del concatenated_strings, string_variable_name, normal_function_name, normal_name, need_more_to_make_the_line_long_enough


# output


# long variable name
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = (
    0
)
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = (
    1  # with a comment
)
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = [
    1,
    2,
    3,
]
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = (
    function()
)
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = function(
    arg1, arg2, arg3
)
this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it = function(
    [1, 2, 3], arg1, [1, 2, 3], arg2, [1, 2, 3], arg3
)
# long function name
normal_name = (
    but_the_function_name_is_now_ridiculously_long_and_it_is_still_super_annoying()
)
normal_name = (
    but_the_function_name_is_now_ridiculously_long_and_it_is_still_super_annoying(
        arg1, arg2, arg3
    )
)
normal_name = (
    but_the_function_name_is_now_ridiculously_long_and_it_is_still_super_annoying(
        [1, 2, 3], arg1, [1, 2, 3], arg2, [1, 2, 3], arg3
    )
)
# long arguments
normal_name = normal_function_name(
    "but with super long string arguments that on their own exceed the line limit so"
    " there's no way it can ever fit",
    "eggs with spam and eggs and spam with eggs with spam and eggs and spam with eggs"
    " with spam and eggs and spam with eggs",
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)
string_variable_name = "a string that is waaaaaaaayyyyyyyy too long, even in parens, there's nothing you can do"  # noqa
for key in """
    hostname
    port
    username
""".split():
    if key in self.connect_kwargs:
        raise ValueError(err.format(key))
concatenated_strings = (
    "some strings that are "
    "concatenated implicitly, so if you put them on separate "
    "lines it will fit"
)
del (
    concatenated_strings,
    string_variable_name,
    normal_function_name,
    normal_name,
    need_more_to_make_the_line_long_enough,
)
