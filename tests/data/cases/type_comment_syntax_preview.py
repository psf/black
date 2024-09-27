# flags: --preview


def f(
    a,  # type: int
):
    pass


# test type comments
def f(a, b, c, d, e, f, g, h, i):
    # type: (int, int, int, int, int, int, int, int, int) -> None
    pass


def f(
    a,  #  type :   int
    b,  #    type :  int
    c,  #type :   int
    d,  #   type:   int
    e,  #              type: int    
    f,  #  type :  int  
    g,  #type:int
    h,  # type: int
    i,  # type: int
):
    # type: (...) -> None
    pass



# output
def f(
    a,  # type: int
):
    pass


# test type comments
def f(a, b, c, d, e, f, g, h, i):
    # type: (int, int, int, int, int, int, int, int, int) -> None
    pass


def f(
    a,  #  type :   int
    b,  #    type :  int
    c,  # type :   int
    d,  # type: int
    e,  # type: int
    f,  #  type :  int
    g,  # type: int
    h,  # type: int
    i,  # type: int
):
    # type: (...) -> None
    pass
