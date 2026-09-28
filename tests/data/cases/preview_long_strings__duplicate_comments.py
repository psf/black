# flags: --unstable
# Regression test for https://github.com/psf/black/issues/3665.
a = b.c(
    d,  # comment
    ("e")
)

x = "aaa\
bbb" + y  # comment

# output
# Regression test for https://github.com/psf/black/issues/3665.
a = b.c(d, "e")  # comment

x = "aaabbb" + y  # comment
