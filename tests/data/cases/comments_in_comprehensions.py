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

# Inline comments on the forced split must not be dropped.
[
    [
        x
        for x
        # comment
        in [  # trailing comment
            # comment
            "ABC"
        ]
    ]
]

[
    [
        x
        for x
        # comment
        in [  # type: ignore[attr-defined]
            # comment
            "ABC"
        ]
    ]
]

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

# Inline comments on the forced split must not be dropped.
[
    [x for x
    # comment
    in [  # trailing comment
    # comment
    "ABC"]]
]

[
    [x for x
    # comment
    in [  # type: ignore[attr-defined]
    # comment
    "ABC"]]
]
