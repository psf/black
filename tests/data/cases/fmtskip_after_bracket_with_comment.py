# A `# fmt: skip` on a line that opens a bracket, combined with a standalone
# comment among the bracket's contents, used to crash inside
# `is_line_short_enough` with `AttributeError: 'Leaf' object has no attribute
# 'bracket_depth'`. The whole statement should now be left untouched.

from m import (
# fmt: skip
    # comment
    a
)

f(
# fmt: skip
    # comment
    a
)

x[
# fmt: skip
    # comment
    a
]

from m import (  # fmt: skip
    # comment
    a
)
