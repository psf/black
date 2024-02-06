# flags: --minimum-version=3.10 --preview

match 1:
    case _ if (True):
        pass


match 1:
    case _ if (
        True
    ):
        pass


# output

match 1:
    case _ if True:
        pass


match 1:
    case _ if True:
        pass
