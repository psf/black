# flags: --preview
a[(1)]
a[(1, 2)]
a[(1,)]
a[()]
a[(x for x in y)]
a[(*x,)]
a[(x := 1,)]
a[((1, 2) + (3, 4))]
a[
    (
        1,
        2,
    )
]
a[
    (
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
    )
]
d[(1, 2,)]
d[
    (
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
    )
]

# We should also handle multidimensional cases
a[:, (1, 2)]
a[(1, 2), :]
a[(1, 2), (3, 4)]
# output
a[1]
a[1, 2]
a[1,]
a[()]
a[(x for x in y)]
a[(*x,)]
a[(x := 1,)]
a[(1, 2) + (3, 4)]
a[
    1,
    2,
]
a[
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
]
d[
    1,
    2,
]
d[
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
]

# We should also handle multidimensional cases
a[:, (1, 2)]
a[(1, 2), :]
a[(1, 2), (3, 4)]
