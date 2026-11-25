# The first line of a class or function body stays attached to its header
# when any individual line is selected via `--line-ranges`.
class A:
    @a
    @b
    def f(self):
        pass

    def g(self):
        pass


class Outer:
    class Inner:
        @dec
        def f(self):
            pass

    @dec
    class Inner2:
        pass


def top():
    @a
    def f():
        pass

    class Inner:
        pass

    return f


class B:
    async def f(self):
        pass

    @dec
    async def g(self):
        pass
