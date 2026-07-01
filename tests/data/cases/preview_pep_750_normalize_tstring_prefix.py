# flags: --preview --minimum-version=3.14

# Uppercase T prefix is normalized to lowercase t in preview style
x = T"bar {1 + 1}"
x = T'bar {1 + 1}'
rT'\{{\}}'

# output

# Uppercase T prefix is normalized to lowercase t in preview style
x = t"bar {1 + 1}"
x = t"bar {1 + 1}"
rt"\{{\}}"
