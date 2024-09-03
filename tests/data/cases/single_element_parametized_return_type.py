def MyClass():
    pass


def create_my_nested_class() -> (
    # test asnkdasldnsalkdnaskldnaklsdnsakln
    int
):
    class MyNestedClass(MyClass):
        pass
    return MyNestedClass


def create_my_nested_class() -> (
    # test asnkdasldnsalkdnaskldnaklsdnsakln
    # test asnkdasldnsalkdnaskldnaklsdnsakln
    int
    # test asnkdasldnsalkdnaskldnaklsdnsakln
):
    class MyNestedClass(MyClass):
        pass
    return MyNestedClass

# output


def MyClass():
    pass


def create_my_nested_class() -> (
    # test asnkdasldnsalkdnaskldnaklsdnsakln
    int
):
    class MyNestedClass(MyClass):
        pass

    return MyNestedClass


def create_my_nested_class() -> (
    # test asnkdasldnsalkdnaskldnaklsdnsakln
    # test asnkdasldnsalkdnaskldnaklsdnsakln
    int
    # test asnkdasldnsalkdnaskldnaklsdnsakln
):
    class MyNestedClass(MyClass):
        pass

    return MyNestedClass
