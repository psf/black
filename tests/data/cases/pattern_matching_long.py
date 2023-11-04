match x:
    case "abcd" | "abcd" | "abcd" :
        pass
    case "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd" | "abcd":
        pass
    case xxxxxxxxxxxxxxxxxxxxxxx:
        pass
    case case:
        pass

# output

match x:
    case "abcd" | "abcd" | "abcd":
        pass
    case (
        "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
        | "abcd"
    ):
        pass
    case xxxxxxxxxxxxxxxxxxxxxxx:
        pass
    case case :
        pass

