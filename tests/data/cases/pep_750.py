# flags: --minimum-version=3.14
x = t"foo"
x = t'foo {{ {2 + 2}bar {{ baz'

x = t"foo {f'abc'} bar"

x = t"""foo {{ a
    foo {2 + 2}bar {{ baz

    x = f"foo {{ {
        2 + 2  # comment
    }bar"

    {{ baz

    }} buzz

    {print("abc" + "def"
)}
abc"""

t'{(abc:=10)}'

t'''This is a really long string, but just make sure that you reflow tstrings {
    2+2:d
}'''
t'This is a really long string, but just make sure that you reflow tstrings correctly {2+2:d}'

t"{     2      +     2    =    }"

t'{
X
!r
}'

tr'\{{\}}'

t'''
    WITH {f'''
    {1}_cte AS ()'''}
'''

t"{'\xFF'}"
t"{r'\xFF'}"
t"{'\xFF'=}"
t"outside \xAA {'\xBB'}"
rt"outside \xAA {'\xBB'}"
t"{f'hello \xEE'}"
t"{'\N{ox}'}"
t"{'\uFaCe'}"
t"{'\U0001F60E'}"
f"{t'hello \xEE'}"
f"""{t"{'\xEE'}"}"""

# output
x = t"foo"
x = t"foo {{ {2 + 2}bar {{ baz"

x = t"foo {f'abc'} bar"

x = t"""foo {{ a
    foo {2 + 2}bar {{ baz

    x = f"foo {{ {
        2 + 2  # comment
    }bar"

    {{ baz

    }} buzz

    {print("abc" + "def"
)}
abc"""

t"{(abc:=10)}"

t"""This is a really long string, but just make sure that you reflow tstrings {
    2+2:d
}"""
t"This is a really long string, but just make sure that you reflow tstrings correctly {2+2:d}"

t"{     2      +     2    =    }"

t"{
X
!r
}"

rt"\{{\}}"

t"""
    WITH {f'''
    {1}_cte AS ()'''}
"""

t"{'\xFF'}"
t"{r'\xFF'}"
t"{'\xFF'=}"
t"outside \xaa {'\xBB'}"
rt"outside \xAA {'\xBB'}"
t"{f'hello \xEE'}"
t"{'\N{ox}'}"
t"{'\uFaCe'}"
t"{'\U0001F60E'}"
f"{t'hello \xee'}"
f"""{t"{'\xEE'}"}"""
