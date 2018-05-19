class ClassSimplest:
    pass
class ClassWithInit:
    def __init__(self):
        pass
class ClassWithInitAndVars:
    cls_var = 100
    def __init__(self):
        pass
class ClassWithInitAndVarsAndDocstring:
    """Test class"""
    cls_var = 100
    def __init__(self):
        pass


# output


class ClassSimplest:
    pass


class ClassWithInit:

    def __init__(self):
        pass


class ClassWithInitAndVars:
    cls_var = 100

    def __init__(self):
        pass


class ClassWithInitAndVarsAndDocstring:
    """Test class"""

    cls_var = 100

    def __init__(self):
        pass
