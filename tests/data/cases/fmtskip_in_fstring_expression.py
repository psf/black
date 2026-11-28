# flags: --minimum-version=3.12
# Regression test for https://github.com/psf/black/issues/5708
# Using `# fmt: skip` inside a multiline f-string replacement field should not
# drop the newline after the comment.

x = f"{
    a+b  # fmt: skip
}"

x = f"{
    # fmt: skip
    a+b
}"

x = f"""{
    a  # fmt: skip
} and {
    b  # fmt: skip
}"""

x = f"""{
    a  # fmt: skip
    + b
}"""

x = f"""{
    a  # fmt: skip

    + b
}"""

x = f"hello {
    a+b  # fmt: skip
} world"

x = f"""{
    (
        foo +
        bar
    )  # fmt: skip
}"""

x = f"""{
    a + b  # fmt: skip
:.2f}"""

x = [
    1,
    2,
    f"{
        a+b  # fmt: skip
    }",
    3,
]


def foo():
    return f"{
        a+b  # fmt: skip
    }"
