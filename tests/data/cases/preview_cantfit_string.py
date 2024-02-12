# flags: --unstable
# long arguments
normal_name = normal_function_name(
    "but with super long string arguments that on their own exceed the line limit so there's no way it can ever fit",
    "eggs with spam and eggs and spam with eggs with spam and eggs and spam with eggs with spam and eggs and spam with eggs",
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)

# output

# long arguments
normal_name = normal_function_name(
    "but with super long string arguments that on their own exceed the line limit so"
    " there's no way it can ever fit",
    "eggs with spam and eggs and spam with eggs with spam and eggs and spam with eggs"
    " with spam and eggs and spam with eggs",
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)
