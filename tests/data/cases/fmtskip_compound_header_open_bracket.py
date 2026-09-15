# Regression tests for https://github.com/psf/black/issues/5402.

if (  # fmt: skip
    cond
):
    pass

while (  # fmt: skip
    cond
):
    pass

for i in (  # fmt: skip
    items
):
    pass

with (  # fmt: skip
    open(  "f"  )
):
    pass

if (  # fmt: skip
    x  ==  "#"
):
    y  =  1

# output

# Regression tests for https://github.com/psf/black/issues/5402.

if (  # fmt: skip
    cond
):
    pass

while (  # fmt: skip
    cond
):
    pass

for i in (  # fmt: skip
    items
):
    pass

with (  # fmt: skip
    open(  "f"  )
):
    pass

if (  # fmt: skip
    x  ==  "#"
):
    y = 1
