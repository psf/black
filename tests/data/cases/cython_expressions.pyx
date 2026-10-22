# flags: --pyx
def f(x):
    a = <int>x
    b = < char * > malloc(10)
    c = <void**>&a
    d = -<int>x + 1
    e = <object>p.q[3]
    g = <np.float64_t*>arr.data
    h = &a
    i = a & b
    j = a<b
    k = foo(<int>x,<double> y)
    return <list>x[0].y(1)
# output
def f(x):
    a = <int>x
    b = <char*>malloc(10)
    c = <void**>&a
    d = -<int>x + 1
    e = <object>p.q[3]
    g = <np.float64_t*>arr.data
    h = &a
    i = a & b
    j = a < b
    k = foo(<int>x, <double>y)
    return <list>x[0].y(1)
