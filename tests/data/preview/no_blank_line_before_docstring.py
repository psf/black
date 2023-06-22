def line_before_docstring():

    """Please move me up"""


class LineBeforeDocstring:

    """Please move me up"""


class EvenIfThereIsAMethodAfter:

    """I'm the docstring"""
    def method(self):
        pass


class TwoLinesBeforeDocstring:


    """I want to be treated the same as if I were closer"""


class MultilineDocstringsAsWell:

    """I'm so far

    and on so many lines...
    """


# output


def line_before_docstring():
    """Please move me up"""


class LineBeforeDocstring:
    """Please move me up"""


class EvenIfThereIsAMethodAfter:
    """I'm the docstring"""

    def method(self):
        pass


class TwoLinesBeforeDocstring:
    """I want to be treated the same as if I were closer"""


class MultilineDocstringsAsWell:
    """I'm so far

    and on so many lines...
    """
