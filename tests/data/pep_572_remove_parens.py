if (foo := 0):
    pass

if (foo := 1):
    pass

if (y := 5 + 5):
    pass

y = (x := 0)

y += (x := 0)

(y := 5 + 5)

test: int = (test2 := 2)

a, b = (test := (1, 2))

# output
if foo := 0:
    pass

if foo := 1:
    pass

if y := 5 + 5:
    pass

y = (x := 0)

y += (x := 0)

(y := 5 + 5)

test: int = (test2 := 2)

a, b = (test := (1, 2))
