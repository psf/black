from typing import NoReturn, Protocol, Union, overload

class Empty:
    ...

def dummy(a): ...
async def other(b): ...


@overload
def a(arg: int) -> int: ...
@overload
def a(arg: str) -> str: ...
@overload
def a(arg: object) -> NoReturn: ...
def a(arg: Union[int, str, object]) -> Union[int, str]:
    if not isinstance(arg, (int, str)):
        raise TypeError
    return arg

class Proto(Protocol):
    def foo(self, a: int) -> int:
        ...

    def bar(self, b: str) -> str: ...
    def baz(self, c: bytes) -> str:
        ...


def dummy_two():
    ...
@dummy
def dummy_three():
    ...

def dummy_four():
    ...

@overload
def b(arg: int) -> int: ...

@overload
def b(arg: str) -> str: ...
@overload
def b(arg: object) -> NoReturn: ...

def b(arg: Union[int, str, object]) -> Union[int, str]:
    if not isinstance(arg, (int, str)):
        raise TypeError
    return arg

def has_comment():
    ...  # still a dummy

if some_condition:
    ...

if already_dummy: ...

class AsyncCls:
    async def async_method(self):
        ...

async def async_function(self):
    ...

@decorated
async def async_function(self):
    ...

class ClassA:
    def f(self):
        
        ...


class ClassB:
    def f(self):
        
        
        
        
        
        
        
        
        
        ...


class ClassC:
    def f(self):
        
        ...
        # Comment


class ClassD:
    def f(self):# Comment 1
        
        ...# Comment 2
        # Comment 3


class ClassE:
    def f(self):
        
        ...
    def f2(self):
        print(10)


class ClassF:
    def f(self):
        
        ...# Comment 2


class ClassG:
    def f(self):#Comment 1
        
        ...# Comment 2
 
       
class ClassH:
    def f(self):
        #Comment

        ...


# output

from typing import NoReturn, Protocol, Union, overload


class Empty: ...


def dummy(a): ...
async def other(b): ...


@overload
def a(arg: int) -> int: ...
@overload
def a(arg: str) -> str: ...
@overload
def a(arg: object) -> NoReturn: ...
def a(arg: Union[int, str, object]) -> Union[int, str]:
    if not isinstance(arg, (int, str)):
        raise TypeError
    return arg


class Proto(Protocol):
    def foo(self, a: int) -> int: ...

    def bar(self, b: str) -> str: ...
    def baz(self, c: bytes) -> str: ...


def dummy_two(): ...
@dummy
def dummy_three(): ...


def dummy_four(): ...


@overload
def b(arg: int) -> int: ...


@overload
def b(arg: str) -> str: ...
@overload
def b(arg: object) -> NoReturn: ...


def b(arg: Union[int, str, object]) -> Union[int, str]:
    if not isinstance(arg, (int, str)):
        raise TypeError
    return arg


def has_comment(): ...  # still a dummy


if some_condition:
    ...

if already_dummy:
    ...


class AsyncCls:
    async def async_method(self): ...


async def async_function(self): ...


@decorated
async def async_function(self): ...


class ClassA:
    def f(self): ...


class ClassB:
    def f(self): ...


class ClassC:
    def f(self):

        ...
        # Comment


class ClassD:
    def f(self):  # Comment 1

        ...  # Comment 2
        # Comment 3


class ClassE:
    def f(self): ...
    def f2(self):
        print(10)


class ClassF:
    def f(self): ...  # Comment 2


class ClassG:
    def f(self):  # Comment 1
        ...  # Comment 2


class ClassH:
    def f(self):
        # Comment

        ...
