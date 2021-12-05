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
        case func(match, case):
            ...
        case another:
            ...


match maybe, multiple:
    case perhaps, 5:
        pass
    case perhaps, 6,:
        pass


match more := (than, one), indeed,:
    case _, (5, 6):
        pass
    case [[5], (6)], [7],:
        pass
    case _:
        pass


match a, *b, c:
    case [*_]:
        assert "seq" == _
    case {}:
        assert "map" == b


match match(
    case,
    match(
        match, case, match, looooooooooooooooooooooooooooooooooooong, match, case, match
    ),
    case,
):
    case case(
        match=case,
        case=re.match(
            loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong
        ),
    ):
        pass

    case [a as match]:
        pass

    case case:
        pass


match match:
    case case:
        pass


match a, *b(), c:
    case d, *f, g:
        pass
