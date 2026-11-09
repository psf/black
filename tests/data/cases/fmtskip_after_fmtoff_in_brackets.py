# `# fmt: skip` on the closing bracket of a `# fmt: off` region, which often ends in a
# comment.

x = [
    # fmt: off
    a,  b  # comment
]  # fmt: skip

x = [
    # fmt: off
    a,  b  # comment
    # fmt: on
]  # fmt: skip

# output

# `# fmt: skip` on the closing bracket of a `# fmt: off` region, which often ends in a
# comment.

x = [
# fmt: off
    a,  b  # comment
]  # fmt: skip

x = [
# fmt: off
    a,  b  # comment
    # fmt: on
]  # fmt: skip
