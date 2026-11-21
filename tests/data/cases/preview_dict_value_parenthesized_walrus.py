# flags: --preview
x = {1: ((a := 1))}
x = {1: (((a := 1)))}
x = {1: (a := 1)}
x = {a: ((b := c)) for a in d}
x = {1: ((a := (yield)))}
# output
x = {1: (a := 1)}
x = {1: (a := 1)}
x = {1: (a := 1)}
x = {a: (b := c) for a in d}
x = {1: (a := (yield))}
