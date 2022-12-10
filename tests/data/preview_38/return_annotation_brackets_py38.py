# Should not remove parens around walrus operator
def walrus() -> (x := 1):
    pass


# output
# Should not remove parens around walrus operator
def walrus() -> (x := 1):
    pass
