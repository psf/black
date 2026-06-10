# flags: --minimum-version=3.10 --line-length=10

match test:
    case case if True:
        pass

# output

match test:
    case (
        case
    ) if True:
        pass
