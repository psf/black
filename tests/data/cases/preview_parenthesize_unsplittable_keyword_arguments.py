# flags: --preview
# Regression test for https://github.com/psf/black/issues/2893

# An unsplittable attribute-chain value now wraps in parentheses.
some_result = some_function(
    long_long_long_long_long_long_long_long_long_long_long_arg=
    long_long_long_long_long_class.long_long_long_long_attr
)

# A splittable operator value also gains a split point after `name=(` (#5335).
foo(
    this_is_a_very_looooooooooooooong_parameter_name=some_very_loooooooooooooooooong_variable_name
    + another_very_loooooooooooooooooong_variable_name
)

# A value with brackets of its own already has a split point and is left alone.
another_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=my_long_dict_variable_name["some_key"],
    long_long_long_long_long_long_long_long_long_long_long_other=some_list[index],
)

# An argument that already fits keeps its operator split.
one_more_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=first_value + second_value,
    long_long_long_long_long_long_long_long_long_long_long_other=some_dict["key"],
)

# A fitting argument is left alone, so it does not disturb the outer layout
# (PR #5592 review regression report).

def check(tmp_venv, simple_poetry, Path, os):
    pth_file = Path("simple_project.pth")
    assert (
        simple_poetry.file.path.parent.resolve().as_posix()
        == tmp_venv.site_packages.find(pth_file)[0]
        .read_text(encoding="utf-8")
        .strip(os.linesep)
    )

# A name so long that `name=(` would still exceed the limit is left alone.
normal_name = normal_function_name(
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)

# Implicitly concatenated string values get parenthesized like any other.
long_tail(
    longer_longer_longer_longer_longer_longer_longer_longer_string_name="one string literal "
    "and another string literal right after it",
)

# The wrap decision uses the argument's own indentation.
def nested_argument():
    if first:
        if second:
            return some_function(
                long_arg_name=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
            )
# output
# Regression test for https://github.com/psf/black/issues/2893

# An unsplittable attribute-chain value now wraps in parentheses.
some_result = some_function(
    long_long_long_long_long_long_long_long_long_long_long_arg=(
        long_long_long_long_long_class.long_long_long_long_attr
    )
)

# A splittable operator value also gains a split point after `name=(` (#5335).
foo(
    this_is_a_very_looooooooooooooong_parameter_name=(
        some_very_loooooooooooooooooong_variable_name
        + another_very_loooooooooooooooooong_variable_name
    )
)

# A value with brackets of its own already has a split point and is left alone.
another_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=my_long_dict_variable_name[
        "some_key"
    ],
    long_long_long_long_long_long_long_long_long_long_long_other=some_list[index],
)

# An argument that already fits keeps its operator split.
one_more_call(
    long_long_long_long_long_long_long_long_long_long_long_arg=first_value
    + second_value,
    long_long_long_long_long_long_long_long_long_long_long_other=some_dict["key"],
)

# A fitting argument is left alone, so it does not disturb the outer layout
# (PR #5592 review regression report).


def check(tmp_venv, simple_poetry, Path, os):
    pth_file = Path("simple_project.pth")
    assert (
        simple_poetry.file.path.parent.resolve().as_posix()
        == tmp_venv.site_packages.find(pth_file)[0]
        .read_text(encoding="utf-8")
        .strip(os.linesep)
    )


# A name so long that `name=(` would still exceed the limit is left alone.
normal_name = normal_function_name(
    this_is_a_ridiculously_long_name_and_nobody_in_their_right_mind_would_use_one_like_it=0,
)

# Implicitly concatenated string values get parenthesized like any other.
long_tail(
    longer_longer_longer_longer_longer_longer_longer_longer_string_name=(
        "one string literal " "and another string literal right after it"
    ),
)


# The wrap decision uses the argument's own indentation.
def nested_argument():
    if first:
        if second:
            return some_function(
                long_arg_name=(
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
                )
            )
