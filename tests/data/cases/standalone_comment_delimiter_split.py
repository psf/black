# Regression tests for https://github.com/psf/black/issues/4026.

import pathlib

short_path = [
    # comment
    pathlib.Path("foo") / "bar" / "baz",
]

fraction = [
    # comment
    23 / 7,
]

short_path_without_trailing_comma = [
    # comment
    pathlib.Path("foo") / "bar" / "baz"
]

fraction_without_trailing_comma = [
    # comment
    23 / 7
]

call_without_trailing_comma = f(
    # comment
    23 / 7
)

grouped_expression = (
    # comment
    23 / 7
)

set_without_trailing_comma = {
    # comment
    23 / 7
}

multiple_elements_without_trailing_comma = [
    # comment
    23 / 7, 42 / 5
]

long_path = [
    # comment
    pathlib.Path("a_very_long_directory_name") / "another_very_long_directory_name" / "a_very_long_filename.txt",
]

long_path_without_trailing_comma = [
    # comment
    pathlib.Path("a_very_long_directory_name") / "another_very_long_directory_name" / "a_very_long_filename.txt"
]

# output

# Regression tests for https://github.com/psf/black/issues/4026.

import pathlib

short_path = [
    # comment
    pathlib.Path("foo") / "bar" / "baz",
]

fraction = [
    # comment
    23 / 7,
]

short_path_without_trailing_comma = [
    # comment
    pathlib.Path("foo") / "bar" / "baz"
]

fraction_without_trailing_comma = [
    # comment
    23 / 7
]

call_without_trailing_comma = f(
    # comment
    23 / 7
)

grouped_expression = (
    # comment
    23 / 7
)

set_without_trailing_comma = {
    # comment
    23 / 7
}

multiple_elements_without_trailing_comma = [
    # comment
    23 / 7,
    42 / 5,
]

long_path = [
    # comment
    pathlib.Path("a_very_long_directory_name")
    / "another_very_long_directory_name"
    / "a_very_long_filename.txt",
]

long_path_without_trailing_comma = [
    # comment
    pathlib.Path("a_very_long_directory_name")
    / "another_very_long_directory_name"
    / "a_very_long_filename.txt"
]
