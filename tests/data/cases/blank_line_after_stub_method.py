# flags: --preview

class Foo:
    def test(): ...
class Bar:
    pass

class Protocol:
    def first(): ...
    def second(): ...
@decorator
class Decorated:
    def method(): ...
def outside():
    pass

class Outer:
    class Inner:
        def method(): ...
    class Sibling:
        pass

# output

class Foo:
    def test(): ...


class Bar:
    pass


class Protocol:
    def first(): ...
    def second(): ...


@decorator
class Decorated:
    def method(): ...


def outside():
    pass


class Outer:
    class Inner:
        def method(): ...

    class Sibling:
        pass
