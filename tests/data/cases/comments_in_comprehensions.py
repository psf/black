# Regression tests for https://github.com/psf/black/issues/4296.

[
    x
    for
    # comment
    x, y in ["AB",]
]

[
    [
        x
        for x
        # comment
        in [
            # comment
            "ABC"
        ]
    ]
]

{
    (
        lambda
        # comment
        x: [
            # comment
        ]
    )
}

async def f():
    return [
        x
        async for
        # comment
        x, y in ["AB",]
    ]

for (a, b), c in [
    # comment
    z,
]:
    pass

# output

# Regression tests for https://github.com/psf/black/issues/4296.

[
    x
    for
    # comment
    x, y in [
        "AB",
    ]
]

[
    [x for x
    # comment
    in [
    # comment
    "ABC"]]
]

{
    lambda
    # comment
    x: [
        # comment
    ]
}


async def f():
    return [
        x
        async for
        # comment
        x, y in [
            "AB",
        ]
    ]


for (a, b), c in [
    # comment
    z,
]:
    pass
