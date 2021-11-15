match something:
    case [a as b]:
        print(b)
    case [a as b, c, d, e as f]:
        print(f)
    case Point(a as b):
        print(b)
    case Point(int() as x, int() as y):
        print(x, y)
