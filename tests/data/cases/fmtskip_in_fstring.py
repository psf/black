# flags: --minimum-version=3.12
# `# fmt: skip` inside f-string replacement fields must keep the newline after
# the comment instead of joining the following token onto the comment line.

x = f"{
    a+b  # fmt: skip
}"

x = f"{a+b  # fmt: skip
}"

x = f"{
    a+b  # fmt: skip
    + c
}"

x = f"{
    a +
    b+c  # fmt: skip
}"

x = f"{
    [
        1+2,  # fmt: skip
        3+4,
    ]
}"

x = f"{
    a+b  # fmt: skip

    + c
}"

x = f"{
    a+b  # fmt: skip

}"

x = f"{
    a+b  # fmt: skip
    # comment 1
    # comment 2
}"

x = f"{
    a+b  # fmt: skip
    =}"

x = f"{
    a+b =  # fmt: skip
}"

x = f"{
    a+b
    # fmt: skip
}"

x = f"{
    a+b
    # fmt: skip
    =}"

x = f"{
    a+b =
    # fmt: skip
}"

x = f"{
    a+b  # fmt: skip
    !r:>10}"

x = f"{val:{
    w+1  # fmt: skip
}}"

x = f"{f'{
    a+b  # fmt: skip
}'}"

x = f"{
    a+b  # fmt: skip
    + c+d  # fmt: skip
}"

x = f"{
    a+b#fmt:skip
}"

x = f"{
    a+b  # fmt: skip
}"  # fmt: skip

x = f"{
    a+b
    # fmt: skip
    =}"  # fmt: skip

# fmt: off
x = f"{
    a+b  # fmt: skip
}"
# fmt: on
