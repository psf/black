x = ("hello") + " world"
f(("a"), b)
f(("only"))
d = {"key": ("value")}
2 * ("" % a)
b + ("" % a)
("pointless")


def foo():
    ("pointless")


# output

x = "hello" + " world"
f("a", b)
f("only")
d = {"key": ("value")}
2 * ("" % a)
b + "" % a
("pointless")


def foo():
    ("pointless")
