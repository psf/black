# flags: --unstable
# A `type: ignore` is recorded per line by the AST, so hugging must not join two
# of them onto one line.
foo(  # type:ignore
    [  # type:ignore
        a
    ]
)

items = [  # type: ignore
    (  # type: ignore
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "longstring"
        else {"key": "val"}
    )
]

# One of them is fine, and so are comments that carry no meaning for the AST.
items = [  # type: ignore
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "longstring"
        else {"key": "val"}
    )
]

func(  # a
    [  # b
        "c",
    ]
)

# output

# A `type: ignore` is recorded per line by the AST, so hugging must not join two
# of them onto one line.
foo(  # type: ignore
    [a]  # type: ignore
)

items = [  # type: ignore
    (  # type: ignore
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "longstring"
        else {"key": "val"}
    )
]

# One of them is fine, and so are comments that carry no meaning for the AST.
items = [  # type: ignore
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "longstring"
    else {"key": "val"}
]

func([  # a  # b
    "c",
])
