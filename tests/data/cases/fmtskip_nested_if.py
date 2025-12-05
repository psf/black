# flags: --preview --no-preview-line-length-1
class ClassWithALongName:
    Constant1 = 1
    Constant2 = 2
    Constant3 = 3


def test():
    if (
        "cond1" == "cond1"
        and "cond2" == "cond2"
        and 1 in (  # fmt: skip
            ClassWithALongName.Constant1,
            ClassWithALongName.Constant2,
            ClassWithALongName.Constant3,
        )
    ):
        return True
    return False

# output

class ClassWithALongName:
    Constant1 = 1
    Constant2 = 2
    Constant3 = 3


def test():
    if (
        "cond1" == "cond1" and "cond2" == "cond2"
        and 1 in (  # fmt: skip
        ClassWithALongName.Constant1,
        ClassWithALongName.Constant2,
        ClassWithALongName.Constant3,
    )
):
        return True
    return False
