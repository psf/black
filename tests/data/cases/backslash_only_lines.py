# A line holding nothing but a backslash continuation must be kept in code that
# Black leaves as written.

# fmt: off
x = [1,
     2] + \
    \
    [3]
# fmt: on

y = [1,2] + \
    \
    [3]  # fmt: skip

if a and \
   \
   b:
    pass

# output
# A line holding nothing but a backslash continuation must be kept in code that
# Black leaves as written.

# fmt: off
x = [1,
     2] + \
    \
    [3]
# fmt: on

y = [1,2] + \
    \
    [3]  # fmt: skip

if a and b:
    pass
