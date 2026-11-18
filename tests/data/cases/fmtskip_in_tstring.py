# flags: --minimum-version=3.14
# `# fmt: skip` inside t-string replacement fields must keep newlines and text verbatim.

x = t"{
    a+b  # fmt: skip
}"

x = t"{a+b  # fmt: skip
}"

x = t"{
    a+b  # fmt: skip
    + c
}"

x = t"{
    [
        1+2,  # fmt: skip
        3+4,
    ]
}"

x = t"{
    a+b  # fmt: skip

    + c
}"

x = t"{
    a+b
    # fmt: skip
}"

x = t"{
    a+b  # fmt: skip
    !r:>10}"

x = t"{val:{
    w+1  # fmt: skip
}}"

x = t"{
    a+b  # fmt: skip
}"  # fmt: skip

x = t"{
    a+b
    # fmt: skip
}"  # fmt: skip
