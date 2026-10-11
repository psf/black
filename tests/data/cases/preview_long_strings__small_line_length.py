# flags: --unstable --line-length=8
l3 = [
    "I have",
    "trailing comma",
    "so I should be braked",
]
t3 = (
    "I have",
    "trailing comma",
    "so I should be braked",
)
s3 = {
    "I have",
    "trailing comma",
    "so I should be braked",
}

# output

l3 = [
    (
        "I have"
    ),
    (
        "trailing comma"
    ),
    (
        "so I should be braked"
    ),
]
t3 = (
    (
        "I have"
    ),
    (
        "trailing comma"
    ),
    (
        "so I should be braked"
    ),
)
s3 = {
    (
        "I have"
    ),
    (
        "trailing comma"
    ),
    (
        "so I should be braked"
    ),
}
