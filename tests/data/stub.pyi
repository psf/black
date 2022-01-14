X: int

def f(): ...


class D: 
    ...


class C:
    ...

class B:
    this_lack_of_newline_should_be_kept: int
    def b(self) -> None: ...

    but_this_newline_should_also_be_kept: int

class A:
    attr: int
    attr2: str

    def f(self) -> int:
        ...

    def g(self) -> str: ...



def g():
    ...

def h(): ...


# output
X: int

def f(): ...

class D: ...
class C: ...

class B:
    this_lack_of_newline_should_be_kept: int
    def b(self) -> None: ...

    but_this_newline_should_also_be_kept: int

class A:
    attr: int
    attr2: str

    def f(self) -> int: ...
    def g(self) -> str: ...

def g(): ...
def h(): ...
