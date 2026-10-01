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
