# flags: --preview

def f(x):
    match x:
        # good refactor
        case [
            y
        ] if y == 123:
            pass

        case [
            y
        ] if True:
            pass

        case [
            y,
        ] if True:
            pass

        # bad refactor
        case [
            y,
        ] if y == 123:
            pass


# output


def f(x):
    match x:
        # good refactor
        case [y] if y == 123:
            pass

        case [y] if True:
            pass

        case [
            y,
        ] if True:
            pass

        # bad refactor
        case [
            y,
        ] if y == 123:
            pass
