# flags: --preview
def foo(
    a, #type:int
    b, #type: str
    c, # type: List[int]
    d, #  type:  Dict[int, str]
    e, #       type:     ignore
    f, # type : ignore
    g, #  type : ignore
):
    pass
    
# output
def foo(
    a,  # type: int
    b,  # type: str
    c,  # type: List[int]
    d,  # type: Dict[int, str]
    e,  # type: ignore
    f,  # type : ignore
    g,  #  type : ignore
):
    pass
