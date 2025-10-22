# flags: --minimum-version=3.14
x = t"foo"
x = t'foo {{ {2 + 2}bar {{ baz'

# output
x = t"foo"
x = t'foo {{ {2 + 2}bar {{ baz'
