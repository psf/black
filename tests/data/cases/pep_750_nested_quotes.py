# flags: --minimum-version=3.14
# Regression test for t-strings whose replacement fields contain quotes.
# Normalising the outer quotes would escape the inner ones and produce a
# t-string that no longer parses, so these are left alone.
x = t'\'{a["b"]}\''
y = t'\'{"x"}\''
# The same applies when the replacement field also carries a backslash.
z = t'\'{a["\n"]}\''
w = t'\'{"\n"}\''
# A backslash in the replacement field stops normalisation on its own, so the
# escaped quote in the literal part is kept as it is.
v = t'{"\n"}\"'
u = t'{a["\n"]}\"'
# t-strings with nothing to escape are still normalised to double quotes.
n = t'{a}'
m = t'{a}\n'

# output

# Regression test for t-strings whose replacement fields contain quotes.
# Normalising the outer quotes would escape the inner ones and produce a
# t-string that no longer parses, so these are left alone.
x = t'\'{a["b"]}\''
y = t'\'{"x"}\''
# The same applies when the replacement field also carries a backslash.
z = t'\'{a["\n"]}\''
w = t'\'{"\n"}\''
# A backslash in the replacement field stops normalisation on its own, so the
# escaped quote in the literal part is kept as it is.
v = t'{"\n"}\"'
u = t'{a["\n"]}\"'
# t-strings with nothing to escape are still normalised to double quotes.
n = t"{a}"
m = t"{a}\n"
