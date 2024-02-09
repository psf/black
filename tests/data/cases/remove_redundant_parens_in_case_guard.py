# flags: --minimum-version=3.10 --preview --line-length=79

match 1:
    case _ if (True):
        pass


match 1:
    case _ if (
        True
    ):
        pass


match 1:
    case _ if (
        # this is a comment
        True
    ):
        pass


match 1:
    case _ if (
        True
        # this is a comment
    ):
        pass


match 1:
    case _ if (
        True  # this is a comment
    ):
        pass


match 1:
    case _ if (  # this is a comment
        True
    ):
        pass


match 1:
    case _ if (
        True
    ):  # this is a comment
        pass


match 1:
    case _ if (True):  # comment over the line limit unless parens are removed x
        pass


match 1:
    case _ if (True):  # comment over the line limit and parens should go to next line
        pass


# output

match 1:
    case _ if True:
        pass


match 1:
    case _ if True:
        pass


match 1:
    case _ if (
        # this is a comment
        True
    ):
        pass


match 1:
    case _ if (
        True
        # this is a comment
    ):
        pass


match 1:
    case _ if True:  # this is a comment
        pass


match 1:
    case _ if True:  # this is a comment
        pass


match 1:
    case _ if True:  # this is a comment
        pass


match 1:
    case _ if True:  # comment over the line limit unless parens are removed x
        pass


match 1:
    case (
        _
    ) if True:  # comment over the line limit and parens should go to next line
        pass
