def f():  # type: ignore
    ...

class x:  # some comment
    ...

class y:
    ...  # comment

# output

def f():  # type: ignore
    ...

class x:  # some comment
    ...

class y: ...  # comment
