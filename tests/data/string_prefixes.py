#!/usr/bin/env python3

name = "Łukasz"
(f"hello {name}", F"hello {name}")
(b"", B"")
(u"", U"")
(r"", R"")

(rf"", fr"", Rf"", fR"", rF"", Fr"", RF"", FR"")
(rb"", br"", Rb"", bR"", rB"", Br"", RB"", BR"")


def docstring_singleline():
    R"""2020 was one hell of a year. The good news is that we were able to"""


def docstring_multiline():
    R"""
    clear out all of the issues opened in that time :p
    """


# output


#!/usr/bin/env python3

name = "Łukasz"
(f"hello {name}", f"hello {name}")
(b"", b"")
("", "")
(r"", R"")

(rf"", rf"", Rf"", Rf"", rf"", rf"", Rf"", Rf"")
(rb"", rb"", Rb"", Rb"", rb"", rb"", Rb"", Rb"")


def docstring_singleline():
    R"""2020 was one hell of a year. The good news is that we were able to"""


def docstring_multiline():
    R"""
    clear out all of the issues opened in that time :p
    """
