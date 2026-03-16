# flags: --minimum-version=3.10


def pattern_matching():
    match status:
        case 1:
            return "1"
        case [single]:
            return "single"
        case [
            action,
            obj,
        ]:
            return "act on obj"
        case Point(x=0):
            return "class pattern"
        case {"text": message}:
            return "mapping"
        case {
            "text": message,
            "format": _,
        }:
            return "mapping"
        case _:
            return "fallback"
