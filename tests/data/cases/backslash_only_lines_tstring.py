# flags: --minimum-version=3.14
# t-strings keep the source of every field, with or without =.
value = 42
x = t"""Value: {value =\
\
}"""
y = t"""{value +\
  \
1}"""
