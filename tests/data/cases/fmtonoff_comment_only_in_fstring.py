# flags: --minimum-version=3.14
# A `# fmt: off` / `# fmt: on` block with only comments in an f-string or t-string
# field. The newline after `# fmt: on` must stay, or the code after it ends up in
# the comment.

x = f"{a
    # fmt: off
    # fmt: on
    + b}"

x = f"{a +
# fmt: off
# fmt: on
b}"

x = f"{
    # comment
    # fmt: off
    # hidden
    # fmt: on
    a}"

print(f"{f(a,
    # fmt: off
    # fmt: on
    b)} {c
    # fmt: off
    # fmt: on
    !r}")

x = f"{a
    # fmt: off
    # fmt: on
=}"

x = f"""{a
  
    # fmt: off
    # fmt: on
    = }"""

x = t"{a
    # fmt: off
    # fmt: on
    + b}"

x = f"{a
    # comment
    # fmt: off
    # fmt: on
    + b}"  # fmt: skip

# fmt: off
x = t"{a
    # fmt: off
    # fmt: on
    + b}"
# fmt: on
