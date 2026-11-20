# flags: --unstable

send(
    "This is a deliberately long positional message that has to be split across lines"
    " so the reader can see where the arguments start and end.",
    "fallback",
)
send(
    "label: " + name,
    "This is a deliberately long positional message that has to be split across lines"
    " so the reader can see where the arguments start and end.",
)
send(
    target,
    "This is a deliberately long positional message that has to be split across lines"
    " so the reader can see where the arguments start and end.",
    label="fallback",
)
send(
    "One " "short argument",
    "fallback",
)


# output
send(
    (
        "This is a deliberately long positional message that has to be split across"
        " lines so the reader can see where the arguments start and end."
    ),
    "fallback",
)
send(
    "label: " + name,
    (
        "This is a deliberately long positional message that has to be split across"
        " lines so the reader can see where the arguments start and end."
    ),
)
send(
    target,
    "This is a deliberately long positional message that has to be split across lines"
    " so the reader can see where the arguments start and end.",
    label="fallback",
)
send(
    "One short argument",
    "fallback",
)
