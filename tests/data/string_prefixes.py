#!/usr/bin/env python3.6

name = R"Łukasz"
F"hello {name}"
B"hello"
r"hello"
fR"hello"


def docstring_singleline():
    R"""2020 was one hell of a year. The good news is that we were able to"""


def docstring_multiline():
    R"""
    clear out all of the issues opened in that time :p
    """


# output


#!/usr/bin/env python3.6

name = R"Łukasz"
f"hello {name}"
b"hello"
r"hello"
fR"hello"


def docstring_singleline():
    R"""2020 was one hell of a year. The good news is that we were able to"""


def docstring_multiline():
    R"""
    clear out all of the issues opened in that time :p
    """
