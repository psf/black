# flags: --minimum-version=3.14
# Regression test for https://github.com/psf/black/issues/5708
# Using `# fmt: skip` inside a multiline t-string replacement field should not
# drop the newline after the comment.

x = t"{
    a+b  # fmt: skip
}"

x = t"{
    # fmt: skip
    a+b
}"

x = t"""{
    a  # fmt: skip
} and {
    b  # fmt: skip
}"""

x = t"""{
    a  # fmt: skip
    + b
}"""
