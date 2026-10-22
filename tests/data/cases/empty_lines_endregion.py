# Regression test for https://github.com/psf/black/issues/3566.
# An `# endregion` marker closes the block above it, so Black must not
# insert the blank lines that separate top-level classes and functions
# before it.
# region Spam
class Foo:
    pass

class Bar:
    pass
# endregion


# region Eggs
class Baz:
    pass

# endregion


def f():
    pass
# endregion


class Outer:
    # region methods
    def method(self):
        pass
    # endregion


x = 1
#endregion
# region Spam
class Bar:
    pass
# endregion
a = 1
# region Ham
class Qux:
    pass
# endregion
def g():
    pass

# output

# Regression test for https://github.com/psf/black/issues/3566.
# An `# endregion` marker closes the block above it, so Black must not
# insert the blank lines that separate top-level classes and functions
# before it.
# region Spam
class Foo:
    pass


class Bar:
    pass
# endregion


# region Eggs
class Baz:
    pass

# endregion


def f():
    pass
# endregion


class Outer:
    # region methods
    def method(self):
        pass
    # endregion


x = 1
# endregion
# region Spam
class Bar:
    pass
# endregion


a = 1


# region Ham
class Qux:
    pass
# endregion


def g():
    pass
