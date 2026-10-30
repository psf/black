# flags: --preview
# Regression test for https://github.com/psf/black/issues/2893

# An unsplittable attribute-chain value now wraps in parentheses.
some_result = some_function(
    long_long_long_long_long_long_long_long_long_long_long_arg=
    long_long_long_long_long_class.long_long_long_long_attr
)

# Values that already fit are unaffected: the binop still splits at the
# operator and the subscript still splits at the brackets.
another_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=first_value + second_value,
    long_long_long_long_long_long_long_long_long_long_long_other=some_dict["key"],
)

# A name so long that `name=(` would still exceed the limit is left alone.
normal_name = normal_function_name(
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)

# A splittable operator value also wraps when the whole argument is too long:
# the value gains its own split point after `name=(` (PR #5592 review, #5335).
foo(
    this_is_a_very_looooooooooooooong_parameter_name=some_very_loooooooooooooooooong_variable_name
    + another_very_loooooooooooooooooong_variable_name
)

# A short argument inside a larger expression is left alone, so the outer
# layout (splitting the assert at the `==`) stays unchanged (PR #5592 review
# regression report).

def check(tmp_venv, simple_poetry, Path, os):
    pth_file = Path("simple_project.pth")
    assert (
        simple_poetry.file.path.parent.resolve().as_posix()
        == tmp_venv.site_packages.find(pth_file)[0]
        .read_text(encoding="utf-8")
        .strip(os.linesep)
    )

# output

# Regression test for https://github.com/psf/black/issues/2893

# An unsplittable attribute-chain value now wraps in parentheses.
some_result = some_function(
    long_long_long_long_long_long_long_long_long_long_long_arg=(
        long_long_long_long_long_class.long_long_long_long_attr
    )
)

# Values that already fit are unaffected: the binop still splits at the
# operator and the subscript still splits at the brackets.
another_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=first_value
    + second_value,
    long_long_long_long_long_long_long_long_long_long_long_other=some_dict["key"],
)

# A name so long that `name=(` would still exceed the limit is left alone.
normal_name = normal_function_name(
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)

# A splittable operator value also wraps when the whole argument is too long:
# the value gains its own split point after `name=(` (PR #5592 review, #5335).
foo(
    this_is_a_very_looooooooooooooong_parameter_name=(
        some_very_loooooooooooooooooong_variable_name
        + another_very_loooooooooooooooooong_variable_name
    )
)

# A short argument inside a larger expression is left alone, so the outer
# layout (splitting the assert at the `==`) stays unchanged (PR #5592 review
# regression report).


def check(tmp_venv, simple_poetry, Path, os):
    pth_file = Path("simple_project.pth")
    assert (
        simple_poetry.file.path.parent.resolve().as_posix()
        == tmp_venv.site_packages.find(pth_file)[0]
        .read_text(encoding="utf-8")
        .strip(os.linesep)
    )
