# flags: --preview --line-length=60
# Regression test for https://github.com/psf/black/issues/4026.

import pathlib

short_path = [
    # comment
    pathlib.Path("foo") / "bar" / "baz"
]

custom_length_path = [
    # comment
    pathlib.Path("long_directory_name") / "another_long_name" / "file.txt"
]

# output
# Regression test for https://github.com/psf/black/issues/4026.

import pathlib

short_path = [
    # comment
    pathlib.Path("foo") / "bar" / "baz"
]

custom_length_path = [
    # comment
    pathlib.Path("long_directory_name")
    / "another_long_name"
    / "file.txt"
]
