# flags: --preview --minimum-version=3.10
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


# output

match maybe, multiple:
    case perhaps, 5:
        pass
    case (
        perhaps,
        6,
    ):
        pass


match more := (than, one), indeed,:
    case _, (5, 6):
        pass
    case (
        [[5], (6)],
        [7],
    ):
        pass
    case _:
        pass