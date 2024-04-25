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

f"{x:{y}d}"

x = f"a{2+2:=^{x}}b"
x = f"a{2+2:=^{foo(x+y**2):something else}}b"
x = f"a{2+2:=^{foo(x+y**2):something else}one more}b"
f'{(abc:=10)}'

f"This is a really long string, but just make sure that you reflow fstrings {
    2+2:d
}"
f"This is a really long string, but just make sure that you reflow fstrings correctly {2+2:d}"

f"{2+2=}"
f"{2+2    =    }"
f"{     2      +     2    =    }"

f"""foo {
    datetime.datetime.now():%Y
%m
%d
}"""

f"{
X
!r
}"

raise ValueError(
                "xxxxxxxxxxxIncorrect --line-ranges format, expect START-END, found"
                f" {lines_str!r}"
            )

f"`escape` only permitted in {{'html', 'latex', 'latex-math'}}, \
got {escape}"

x = f'\N{GREEK CAPITAL LETTER DELTA} \N{SNOWMAN} {x}'
fr'\{{\}}'

f"""
    WITH {f'''
    {1}_cte AS ()'''}
"""

value: str = f'''foo
'''

log(
    f"Received operation {server_operation.name} from "
    f"{self.writer._transport.get_extra_info('peername')}",  # type: ignore[attr-defined]
    level=0,
)

f"{1:{f'{2}'}}"
f'{1:{f'{2}'}}'
f'{1:{2}d}'

f'{{\\"kind\\":\\"ConfigMap\\",\\"metadata\\":{{\\"annotations\\":{{}},\\"name\\":\\"cluster-info\\",\\"namespace\\":\\"amazon-cloudwatch\\"}}}}'

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

rf"foo"
rf"{foo}"

f"{x:{y}d}"

x = f"a{2+2:=^{x}}b"
x = f"a{2+2:=^{foo(x+y**2):something else}}b"
x = f"a{2+2:=^{foo(x+y**2):something else}one more}b"
f"{(abc:=10)}"

f"This is a really long string, but just make sure that you reflow fstrings {
    2+2:d
}"
f"This is a really long string, but just make sure that you reflow fstrings correctly {2+2:d}"

f"{2+2=}"
f"{2+2    =    }"
f"{     2      +     2    =    }"

f"""foo {
    datetime.datetime.now():%Y
%m
%d
}"""

f"{
X
!r
}"

raise ValueError(
    "xxxxxxxxxxxIncorrect --line-ranges format, expect START-END, found"
    f" {lines_str!r}"
)

f"`escape` only permitted in {{'html', 'latex', 'latex-math'}}, \
got {escape}"

x = f"\N{GREEK CAPITAL LETTER DELTA} \N{SNOWMAN} {x}"
rf"\{{\}}"

f"""
    WITH {f'''
    {1}_cte AS ()'''}
"""

value: str = f"""foo
"""

log(
    f"Received operation {server_operation.name} from "
    f"{self.writer._transport.get_extra_info('peername')}",  # type: ignore[attr-defined]
    level=0,
)

f"{1:{f'{2}'}}"
f"{1:{f'{2}'}}"
f"{1:{2}d}"

f'{{\\"kind\\":\\"ConfigMap\\",\\"metadata\\":{{\\"annotations\\":{{}},\\"name\\":\\"cluster-info\\",\\"namespace\\":\\"amazon-cloudwatch\\"}}}}'
