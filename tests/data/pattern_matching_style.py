match something:
    case b(): print(1+1)
    case c(
        very_complex=True,
        perhaps_even_loooooooooooooooooooooooooooooooooooooong=-   1
    ): print(1)
    case c(
        very_complex=True,
        perhaps_even_loooooooooooooooooooooooooooooooooooooong=-1
    ): print(2)
    case a: pass

# output

match something:
    case b():
        print(1 + 1)
    case c(
        very_complex=True, perhaps_even_loooooooooooooooooooooooooooooooooooooong=-1
    ):
        print(1)
    case c(
        very_complex=True, perhaps_even_loooooooooooooooooooooooooooooooooooooong=-1
    ):
        print(2)
    case a:
        pass
