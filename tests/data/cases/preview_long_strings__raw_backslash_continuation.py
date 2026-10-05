# flags: --unstable
# In a raw string, a backslash followed by a newline is part of the string's
# value, so it must not be removed like a line continuation.
x = r"abc\
def"

y = rb'abc\
def'

z = Rf"{x}\
def"

w = "abc\
def"

# output
# In a raw string, a backslash followed by a newline is part of the string's
# value, so it must not be removed like a line continuation.
x = r"abc\
def"

y = rb"abc\
def"

z = Rf"{x}\
def"

w = "abcdef"
