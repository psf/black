# Regression tests for https://github.com/psf/black/issues/4513.
# Fixed by #4903 ("Improve fmt:skip handling in nested expressions with checks").
# Each of the three inputs below used to crash with a "Cannot parse" error.

# Case A: triple-quoted string inside parens with a leading `# fmt: skip` line.
(
# fmt: skip
"""
"""
)

# Case B: line-continued string inside parens with a leading `# fmt: skip` line.
(
# fmt: skip
"\
"
)

# Case C: `# fmt: skip` on the opening paren of a comparator expression.
foo = (  # fmt: skip
    some_long_expression
    > some_other_long_expression
)

# output

# Regression tests for https://github.com/psf/black/issues/4513.
# Fixed by #4903 ("Improve fmt:skip handling in nested expressions with checks").
# Each of the three inputs below used to crash with a "Cannot parse" error.

# Case A: triple-quoted string inside parens with a leading `# fmt: skip` line.
(
# fmt: skip
"""
"""
)

# Case B: line-continued string inside parens with a leading `# fmt: skip` line.
(
# fmt: skip
"\
"
)

# Case C: `# fmt: skip` on the opening paren of a comparator expression.
foo = (  # fmt: skip
    some_long_expression
    > some_other_long_expression
)
