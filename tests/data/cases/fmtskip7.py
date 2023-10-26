a =     "this is some code"
b =     5  #fmt:skip
c = 9  #fmt: skip
d = "thisisasuperlongstringthisisasuperlongstringthisisasuperlongstringthisisasuperlongstring"  #fmt:skip

if True: print("yay")  # fmt: skip
class Foo: ...  # fmt: skip

# output

a = "this is some code"
b =     5  # fmt:skip
c = 9  # fmt: skip
d = "thisisasuperlongstringthisisasuperlongstringthisisasuperlongstringthisisasuperlongstring"  # fmt:skip

if True: print("yay")  # fmt: skip
class Foo: ...  # fmt: skip
