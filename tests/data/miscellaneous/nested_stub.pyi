import sys

class Outer:
    class InnerStub: ...
    outer_attr_after_inner_stub: int
    class Inner:
        inner_attr: int
    outer_attr: int

if sys.version_info > (3, 7):
    if sys.platform == "win32":
        assignment = 1
        def function_definition(self): ...
    def f1(self) -> str: ...
    if sys.platform != "win32":
        def function_definition(self): ...
        assignment = 1
    def f2(self) -> str: ...

# output

import sys

class Outer:
    class InnerStub: ...
    outer_attr_after_inner_stub: int

    class Inner:
        inner_attr: int

    outer_attr: int

if sys.version_info > (3, 7):
    if sys.platform == "win32":
        assignment = 1
        def function_definition(self): ...

    def f1(self) -> str: ...
    if sys.platform != "win32":
        def function_definition(self): ...
        assignment = 1

    def f2(self) -> str: ...