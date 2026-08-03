# flags: --minimum-version=3.14
def tea():
    t" not a docstring"

def tea2():
    t' also not a docstring'

def triple_quoted_template():
    t"""   not a docstring   """

def triple_quoted_template2():
    t'''
      also not a docstring
      '''

def raw_template():
    rt"  not a docstring  "

def capitalized_template():
    T" NOT A DOCSTRING"

class Pot:
    t"  not a docstring either  "

t"  module level, still not a docstring  "

# output
def tea():
    t" not a docstring"


def tea2():
    t" also not a docstring"


def triple_quoted_template():
    t"""   not a docstring   """


def triple_quoted_template2():
    t"""
      also not a docstring
      """


def raw_template():
    rt"  not a docstring  "


def capitalized_template():
    T" NOT A DOCSTRING"


class Pot:
    t"  not a docstring either  "


t"  module level, still not a docstring  "
