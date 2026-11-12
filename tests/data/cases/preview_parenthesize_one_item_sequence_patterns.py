# flags: --preview
match command:
    case "exit",:
        pass
    case *rest,:
        pass
    case "quit" as action,:
        pass
    case "help", if verbose:
        pass
    case ("exit",):
        pass
    case ["exit"]:
        pass
    case "help", "comma":
        pass


# output
match command:
    case ("exit",):
        pass
    case (*rest,):
        pass
    case ("quit" as action,):
        pass
    case ("help",) if verbose:
        pass
    case ("exit",):
        pass
    case ["exit"]:
        pass
    case "help", "comma":
        pass
