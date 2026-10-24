# flags: --preview --line-length 30

# Regression test: at a short line length the second formatting pass used to
# lose the `fmt: skip` marker of the hidden code, split before the `|` operator
# and produce a line starting with ` | {`, which is not valid Python.

y = {  # fmt: skip
    "a": 1} | {"b": 2}

# output

# Regression test: at a short line length the second formatting pass used to
# lose the `fmt: skip` marker of the hidden code, split before the `|` operator
# and produce a line starting with ` | {`, which is not valid Python.

y = {  # fmt: skip
    "a": 1} | {
    "b": 2
}
