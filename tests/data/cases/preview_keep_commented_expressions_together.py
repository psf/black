# flags: --preview --line-length=88

# Regression test for https://github.com/psf/black/issues/4026
# and https://github.com/psf/black/issues/3713
# When a bracketed collection or call contains a standalone comment before
# an expression with delimiters (binary operators, comparisons, comprehensions),
# the expression should not be unnecessarily broken across lines if it fits
# within the line length limit.

fizzbuzz = [
    # comment
    23 / 7
]

foobar = [
    # comment
    pathlib.Path("foo") / "bar" / "baz",
]

func(
    # comment
    a * b
)

bitwise = [
    # comment
    flags | MASK_ONE & ~MASK_TWO,
]

comprehension = [
    # comment
    a for a in []
]

comparison = [
    # comment
    True == False
]

logical = [
    # comment
    a and b
]

ternary = [
    # comment
    a if b else c
]

multi = [
    # comment
    23 / 7,
    pathlib.Path("a") / "b",
]

multi_split = [
    # comment
    1, 2, 3
]

long_expr = [
    # comment
    pathlib.Path("foo_very_long_path_name_that_exceeds_the_line_length_limit_and_needs_to_be_split") / "bar" / "baz",
]

# Regression test for https://github.com/psf/black/issues/638
# A standalone comment inside parentheses around a comparison must not
# fragment the comparison, wherever the comment sits.
paren_comparison = (
    # comment
    1 == 2
)

trailing_comment = (
    1 == 2
    # comment
)

if (
    # comment
    1 == 2
):
    pass

if (
    1 == 2
    # comment
):
    pass

comment_between_operands = (
    1 ==
    # comment
    2
)

long_trailing_comment = (
    pathlib.Path("foo_very_long_path_name_that_exceeds_the_line_length_limit_and_needs") == "bar"
    # comment
)

list_trailing_comment = [
    1 == 2,
    # comment
]

# output

# Regression test for https://github.com/psf/black/issues/4026
# and https://github.com/psf/black/issues/3713
# When a bracketed collection or call contains a standalone comment before
# an expression with delimiters (binary operators, comparisons, comprehensions),
# the expression should not be unnecessarily broken across lines if it fits
# within the line length limit.

fizzbuzz = [
    # comment
    23 / 7
]

foobar = [
    # comment
    pathlib.Path("foo") / "bar" / "baz",
]

func(
    # comment
    a * b
)

bitwise = [
    # comment
    flags | MASK_ONE & ~MASK_TWO,
]

comprehension = [
    # comment
    a for a in []
]

comparison = [
    # comment
    True == False
]

logical = [
    # comment
    a and b
]

ternary = [
    # comment
    a if b else c
]

multi = [
    # comment
    23 / 7,
    pathlib.Path("a") / "b",
]

multi_split = [
    # comment
    1,
    2,
    3,
]

long_expr = [
    # comment
    pathlib.Path(
        "foo_very_long_path_name_that_exceeds_the_line_length_limit_and_needs_to_be_split"
    )
    / "bar"
    / "baz",
]

# Regression test for https://github.com/psf/black/issues/638
# A standalone comment inside parentheses around a comparison must not
# fragment the comparison, wherever the comment sits.
paren_comparison = (
    # comment
    1 == 2
)

trailing_comment = (
    1 == 2
    # comment
)

if (
    # comment
    1 == 2
):
    pass

if (
    1 == 2
    # comment
):
    pass

comment_between_operands = (
    1 ==
    # comment
    2
)

long_trailing_comment = (
    pathlib.Path("foo_very_long_path_name_that_exceeds_the_line_length_limit_and_needs")
    == "bar"
    # comment
)

list_trailing_comment = [
    1 == 2,
    # comment
]
