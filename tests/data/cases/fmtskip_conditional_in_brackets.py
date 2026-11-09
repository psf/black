x = (
    a + b if c else d,  # fmt: skip
    (e),
)

y = {
    k: a + b if c else d,  # fmt: skip
    j: (e),
}

z = (
    a.b if c else d,  # fmt: skip
    e,
)

w = (
    a  +  b if c else d,  # fmt: skip
    (e),
)


def limit_offset_sql(limit, offset):
    return " ".join(
        sql
        for sql in (
            "LIMIT %d" % limit if limit else None,  # fmt: skip
            ("OFFSET %d" % offset) if offset else None,
        )
        if sql
    )


# The conditional expression starts on an earlier line, so the skipped code on the
# last line ends the expression and takes the comma after it along.
x = (
    a
    if c else d,  # fmt: skip
    e,
)

x = (
    a  # comment
    + b if c else d,  # fmt: skip
    (e),
)

foo(
    a
    or b if c else d,  # fmt: skip
    e,
)
