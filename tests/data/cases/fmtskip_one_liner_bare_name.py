# `# fmt: skip` on a one-line compound statement whose semicolon-separated body
# starts with a bare name. The header must only be kept once.
if True: a; b  # fmt: skip
while x: a; b  # fmt: skip
for i in r: i; print(i)  # fmt: skip
with a: b; c  # fmt: skip
def f(): x; return x  # fmt: skip
def g(a, b=1) -> int: a; return b  # fmt: skip
class A: x; y = 1  # fmt: skip
z  =  1

# output
# `# fmt: skip` on a one-line compound statement whose semicolon-separated body
# starts with a bare name. The header must only be kept once.
if True: a; b  # fmt: skip
while x: a; b  # fmt: skip
for i in r: i; print(i)  # fmt: skip
with a: b; c  # fmt: skip
def f(): x; return x  # fmt: skip
def g(a, b=1) -> int: a; return b  # fmt: skip
class A: x; y = 1  # fmt: skip
z = 1
