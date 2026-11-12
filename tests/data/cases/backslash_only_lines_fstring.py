# flags: --minimum-version=3.12
# f-string fields are written back as is. With `=`, the source of the field is
# part of the string, so a line holding nothing but a backslash must be kept.
value = 42
z = f"""{value =\
\
}"""
w = f"""{value =\
  \
}"""
v = f"""{value +\
\
1}"""
