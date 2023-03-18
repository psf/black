class Outer:
    class InnerStub: ...
    outer_attr_after_inner_stub: int
    class Inner:
        inner_attr: int
    outer_attr: int

# output
class Outer:
    class InnerStub: ...
    outer_attr_after_inner_stub: int

    class Inner:
        inner_attr: int

    outer_attr: int
