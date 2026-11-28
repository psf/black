# flags: --minimum-version=3.14
# `# fmt: skip` inside an f-string or t-string replacement field.
# The newline after `# fmt: skip` must stay intact so following tokens are not commented out.

x = f"{
    a+b  # fmt: skip
}"

x = f"{
    a+b  # fmt: skip
    + c
}"

x = f"{
    a+b
    # fmt: skip
    =}"

x = f"{
    a+b  # fmt: skip
!r}"

x = f"{
    a+b  # fmt: skip
:10}"

x = f"{val:{
    w+1  # fmt: skip
}}"

x = t"{
    a+b  # fmt: skip
}"

x = t"{
    a+b
    # fmt: skip
}"

x = f"{
    a   +   1  # fmt: skip
    + b   +   2  # fmt: skip
}"
