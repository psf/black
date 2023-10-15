# flags: --minimum-version=3.12
x = f"foo"
x = f'foo'
x = f"""foo"""
x = f'''foo'''
x = f"foo {{ bar {{ baz"
x = f"foo {{ {2 + 2}bar {{ baz"
x = f'foo {{ {2 + 2}bar {{ baz'
x = f"""foo {{ {2 + 2}bar {{ baz"""
x = f'''foo {{ {2 + 2}bar {{ baz'''

# edge case: FSTRING_MIDDLE containing only whitespace should not be stripped
x = f"{a} {b}"

x = f"foo {
    2 + 2
} bar baz"

x = f"foo {{ {"a  {2 + 2}  b"}bar {{ baz"
x = f"foo {{ {f'a  {2 + 2}  b'}bar {{ baz"
x = f"foo {{ {f"a  {2 + 2}  b"}bar {{ baz"

x = f"foo {{ {f'a  {f"a  {2 + 2}  b"}  b'}bar {{ baz"
x = f"foo {{ {f"a  {f"a  {2 + 2}  b"}  b"}bar {{ baz"

x = """foo {{ {2 + 2}bar
baz"""


x = f"""foo {{ {2 + 2}bar {{ baz"""

x = f"""foo {{ {
    2 + 2
}bar {{ baz"""


x = f"""foo {{ {
    2 + 2
}bar
baz"""

x = f"""foo {{ a
    foo {2 + 2}bar {{ baz

    x = f"foo {{ {
        2 + 2  # comment
    }bar"

    {{ baz

    }} buzz

    {print("abc" + "def"
)}
abc"""

# edge case: end triple quotes at index zero
f"""foo {2+2} bar
"""

f' \' {f"'"} \' '
f" \" {f'"'} \" "

x = f"a{2+2:=^72}b"
x = f"a{2+2:x}b"

rf'foo'
rf'{foo}'

x = f"a{2+2:=^{x}}b"
x = f"a{2+2:=^{foo(x+y**2):something else}}b"
f'{(abc:=10)}'

f"This is a really long string, but just make sure that you reflow fstrings {
    2+2:d
}"
f"This is a really long string, but just make sure that you reflow fstrings correctly {2+2:d}"

# TODO: Edge case: if the fstring replacement ends with a `=` it should not be touched
# f"{2+2=}"
# f"{2+2    =    }"
# f"{     2      +     2    =    }"

# TODO:
# f"""foo {
#     datetime.datetime.now():%Y
# %m
# %d
# }"""

# output

x = f"foo"
x = f"foo"
x = f"""foo"""
x = f"""foo"""
x = f"foo {{ bar {{ baz"
x = f"foo {{ {2 + 2}bar {{ baz"
x = f"foo {{ {2 + 2}bar {{ baz"
x = f"""foo {{ {2 + 2}bar {{ baz"""
x = f"""foo {{ {2 + 2}bar {{ baz"""

# edge case: FSTRING_MIDDLE containing only whitespace should not be stripped
x = f"{a} {b}"

x = f"foo {2 + 2} bar baz"

x = f"foo {{ {"a  {2 + 2}  b"}bar {{ baz"
x = f"foo {{ {f"a  {2 + 2}  b"}bar {{ baz"
x = f"foo {{ {f"a  {2 + 2}  b"}bar {{ baz"

x = f"foo {{ {f"a  {f"a  {2 + 2}  b"}  b"}bar {{ baz"
x = f"foo {{ {f"a  {f"a  {2 + 2}  b"}  b"}bar {{ baz"

x = """foo {{ {2 + 2}bar
baz"""


x = f"""foo {{ {2 + 2}bar {{ baz"""

x = f"""foo {{ {2 + 2}bar {{ baz"""


x = f"""foo {{ {
    2 + 2
}bar
baz"""

x = f"""foo {{ a
    foo {
    2 + 2
}bar {{ baz

    x = f"foo {{ {
    2 + 2  # comment
}bar"

    {{ baz

    }} buzz

    {
    print("abc" + "def")
}
abc"""

# edge case: end triple quotes at index zero
f"""foo {
    2 + 2
} bar
"""

f" ' {f"'"} ' "
f' " {f'"'} " '

x = f"a{2 + 2:=^72}b"
x = f"a{2 + 2:x}b"

rf"foo"
rf"{foo}"

x = f"a{2 + 2:=^{x}}b"
x = f"a{2 + 2:=^{foo(x + y**2):something else}}b"
f"{(abc := 10)}"

f"This is a really long string, but just make sure that you reflow fstrings {2 + 2:d}"
f"This is a really long string, but just make sure that you reflow fstrings correctly {
    2 + 2:d
}"

# TODO: Edge case: if the fstring replacement ends with a `=` it should not be touched
# f"{2+2=}"
# f"{2+2    =    }"
# f"{     2      +     2    =    }"

# TODO:
# f"""foo {
#     datetime.datetime.now():%Y
# %m
# %d
# }"""
