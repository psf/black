def foo(e):
    f""" {'.'.join(e)}"""

def bar(e):
    f"{'.'.join(e)}"

def baz(e):
    F""" {'.'.join(e)}"""

# output
def foo(e):
    f""" {'.'.join(e)}"""


def bar(e):
    f"{'.'.join(e)}"


def baz(e):
    f""" {'.'.join(e)}"""
