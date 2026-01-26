# Explicit backslash continuation without indentation (issue #4945)

if True:
    foo = 1+\
2
    print(foo)

#Output

if True:
    foo = 1 + 2
    print(foo)
