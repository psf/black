import match

match something:
    case [a as b]:
        print(b)
    case [a as b, c, d, e as f]:
        print(f)
    case Point(a as b):
        print(b)
    case Point(int() as x, int() as y):
        print(x, y)


match = 1
case: int = re.match(something)

match re.match(case):
    case type("match", match):
        pass
    case match:
        pass


def func(match: case, case: match) -> case:
    match Something():
        case another:
            ...
        case func(match, case):
            ...
