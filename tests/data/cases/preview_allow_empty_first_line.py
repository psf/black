# flags: --preview
def foo():
    """
    Docstring
    """

    # Here we go
    if x:

        # This is also now fine
        a = 123

    else:
        # But not necessary
        a = 123

    if y:

        while True:

            """
            Long comment here
            """
            a = 123
    
    if z:

        for _ in range(100):
            a = 123
    else:

        try:

            # this should be ok
            a = 123
        except:

            """also this"""
            a = 123


def bar():

    if x:
        a = 123


def baz():

    # OK
    if x:
        a = 123

def quux():

    new_line = here


class Cls:

    def method(self):

        pass

# output

def foo():
    """
    Docstring
    """

    # Here we go
    if x:

        # This is also now fine
        a = 123

    else:
        # But not necessary
        a = 123

    if y:

        while True:

            """
            Long comment here
            """
            a = 123

    if z:

        for _ in range(100):
            a = 123
    else:

        try:

            # this should be ok
            a = 123
        except:

            """also this"""
            a = 123


def bar():

    if x:
        a = 123


def baz():

    # OK
    if x:
        a = 123


def quux():

    new_line = here


class Cls:
    def method(self):

        pass
