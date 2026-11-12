# A comment-only `# fmt: off` / `# fmt: on` block right before an assignment to a
# tuple used to get more blank lines before it on every pass.
a = 1
# fmt: off
# fmt: on
b,  c = d
# fmt: off
#   keep  this
# fmt: on
(e, f) = g
# fmt: off
# fmt: on
*h, i = j
def k():
    x = 1
    # fmt: off
    # fmt: on
    y, = z

# output

# A comment-only `# fmt: off` / `# fmt: on` block right before an assignment to a
# tuple used to get more blank lines before it on every pass.
a = 1
# fmt: off
# fmt: on
b, c = d
# fmt: off
#   keep  this
# fmt: on
(e, f) = g
# fmt: off
# fmt: on
*h, i = j


def k():
    x = 1
    # fmt: off
    # fmt: on
    y, = z
