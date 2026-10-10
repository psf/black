# Regression tests for https://github.com/psf/black/issues/5402.
# `# fmt: skip` on an opening bracket of a compound statement header made
# `_force_standalone_comment_split` isolate the header `:` on its own line,
# producing unparseable output (InvalidInput). The header `:` is now kept with
# the comment line.

if (  # fmt: skip
    cond
):
    pass
elif (  # fmt: skip
    other_cond
):
    pass

while (  # fmt: skip
    cond
):
    pass

for x in (  # fmt: skip
    items
):
    pass

with (  # fmt: skip
    open("f")
):
    pass

try:
    pass
except (  # fmt: skip
    ValueError, TypeError
):
    pass


async def test_async():
    async for x in (  # fmt: skip
        items
    ):
        pass

    async with (  # fmt: skip
        open("f")
    ):
        pass


match (  # fmt: skip
    val
):
    case (  # fmt: skip
        1, 2
    ):
        pass
