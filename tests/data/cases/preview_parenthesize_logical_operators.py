# flags: --preview

# Issue #3629: Parenthesize logical expressions with function calls

very_very_very_very_very_very_very_very_long_expression = "foo"
if isinstance(very_very_very_very_very_very_very_very_long_expression, Sequence) and not isinstance(
    very_very_very_very_very_very_very_very_long_expression, str
):
    print("foo")


def _is_onnx_list(value):
    return not isinstance(value, (str, bytes, torch.Tensor)) and isinstance(
        value, Iterable
    )


while check_first_very_long_condition(arg1, arg2) or check_second_very_long_condition(arg3, arg4):
    pass


b = self.same_name_function(left, reference_list) and self.same_name_function(
    right, reference_list
)

# Short condition that fits within line length should remain on one line
if isinstance(x, int) and not isinstance(y, str):
    pass

# output

# Issue #3629: Parenthesize logical expressions with function calls

very_very_very_very_very_very_very_very_long_expression = "foo"
if (
    isinstance(very_very_very_very_very_very_very_very_long_expression, Sequence)
    and not isinstance(very_very_very_very_very_very_very_very_long_expression, str)
):
    print("foo")


def _is_onnx_list(value):
    return (
        not isinstance(value, (str, bytes, torch.Tensor))
        and isinstance(value, Iterable)
    )


while (
    check_first_very_long_condition(arg1, arg2)
    or check_second_very_long_condition(arg3, arg4)
):
    pass


b = (
    self.same_name_function(left, reference_list)
    and self.same_name_function(right, reference_list)
)

# Short condition that fits within line length should remain on one line
if isinstance(x, int) and not isinstance(y, str):
    pass
