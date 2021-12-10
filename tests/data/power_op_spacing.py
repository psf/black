def function(**kwargs):
    t = a**2 + b**3
    return t ** 2


def function_replace_spaces(**kwargs):
    t = a **2 + b** 3 + c ** 4


def function_dont_replace_spaces():
    {**a, **b, **c}


a = 5**~4
b = 5 ** f()
c = -(5**2)
d = 5 ** f["hi"]
e = lazy(lambda **kwargs: 5)
f = f() ** 5
g = a.b**c.d
h = 5 ** funcs.f()
i = funcs.f() ** 5
j = super().name ** 5
k = [(2**idx, value) for idx, value in pairs]
l = mod.weights_[0] == pytest.approx(0.95**100, abs=0.001)
m = [([2**63], [1, 2**63])]
n = count <= 10**5
o = settings(max_examples=10**6)
p = {(k, k**2): v**2 for k, v in pairs}
q = [10**i for i in range(6)]


# output


def function(**kwargs):
    t = a**2 + b**3
    return t**2


def function_replace_spaces(**kwargs):
    t = a**2 + b**3 + c**4


def function_dont_replace_spaces():
    {**a, **b, **c}


a = 5**~4
b = 5 ** f()
c = -(5**2)
d = 5 ** f["hi"]
e = lazy(lambda **kwargs: 5)
f = f() ** 5
g = a.b**c.d
h = 5 ** funcs.f()
i = funcs.f() ** 5
j = super().name ** 5
k = [(2**idx, value) for idx, value in pairs]
l = mod.weights_[0] == pytest.approx(0.95**100, abs=0.001)
m = [([2**63], [1, 2**63])]
n = count <= 10**5
o = settings(max_examples=10**6)
p = {(k, k**2): v**2 for k, v in pairs}
q = [10**i for i in range(6)]
