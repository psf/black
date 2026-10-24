# flags: --preview

# splits: every literal ending in a newline gets its own line (#1540)
ValueError("Invalid input:\n" f" * x={x}\n" f" * y={y}\n" f" * z={z}")
h(f"{x}\n" f"{y}")
f("x\n" "y", "z")
f("a\n" "b")  # comment
i("""abc
""" "tail")

# mixed: breaks only after the literals that end in a newline
g("intro:\n" f"{a}" f" mid\n" f"{b}")

# no split: no literal ends in a newline
f("Data: " f"{foo: <4} | " f"{bar:8d} | " f"{qux: >16}")
f(r"raw\n" "tail")
f("path\\n" "tail")

# no split: single string, no concatenation
ValueError(f"Invalid input:\n * x={x}\n * y={y}\n * z={z}")
f("aaabbb")  # comment
f("aaabbb", "ccc")
f(g("aabb"))

# no split: concatenation treated as a single atom
x = "a\n" "b"
d = {"key": "x\n" "y"}
msg = (
    "Instructions:\n"
    " 1) ..."
)

# long concatenation without newlines: right-hand split, literals stay joined
f("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" "cccccccccccccccccccccccccccccccccccccccc")

# long assignment RHS: parens kept, literals split
msg = ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n" "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n" "cccc")

# already split: stable
ValueError(
    "Invalid input:\n"
    f" * x={x}\n"
    f" * y={y}\n"
    f" * z={z}"
)
f(
    "x\n"
    "y",
    "z"
)
f(
    "aaabbb",
)

# nested brackets cascade
outer(g("a\n" "b"), "c\n" "d")

# output

# splits: every literal ending in a newline gets its own line (#1540)
ValueError(
    "Invalid input:\n"
    f" * x={x}\n"
    f" * y={y}\n"
    f" * z={z}"
)
h(
    f"{x}\n"
    f"{y}"
)
f(
    "x\n"
    "y",
    "z"
)
f(
    "a\n"
    "b"
)  # comment
i(
    """abc
"""
    "tail"
)

# mixed: breaks only after the literals that end in a newline
g(
    "intro:\n"
    f"{a}" f" mid\n"
    f"{b}"
)

# no split: no literal ends in a newline
f("Data: " f"{foo: <4} | " f"{bar:8d} | " f"{qux: >16}")
f(r"raw\n" "tail")
f("path\\n" "tail")

# no split: single string, no concatenation
ValueError(f"Invalid input:\n * x={x}\n * y={y}\n * z={z}")
f("aaabbb")  # comment
f("aaabbb", "ccc")
f(g("aabb"))

# no split: concatenation treated as a single atom
x = "a\n" "b"
d = {"key": "x\n" "y"}
msg = "Instructions:\n" " 1) ..."

# long concatenation without newlines: right-hand split, literals stay joined
f(
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    "cccccccccccccccccccccccccccccccccccccccc"
)

# long assignment RHS: parens kept, literals split
msg = (
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
    "cccc"
)

# already split: stable
ValueError(
    "Invalid input:\n"
    f" * x={x}\n"
    f" * y={y}\n"
    f" * z={z}"
)
f(
    "x\n"
    "y",
    "z"
)
f(
    "aaabbb",
)

# nested brackets cascade
outer(
    g(
        "a\n"
        "b"
    ),
    "c\n"
    "d"
)
