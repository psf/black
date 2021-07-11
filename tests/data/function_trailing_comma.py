def f(a,):
    d = {'key': 'value',}
    tup = (1,)

def f2(a,b,):
    d = {'key': 'value', 'key2': 'value2',}
    tup = (1,2,)

def f(a:int=1,):
    call(arg={'explode': 'this',})
    call2(arg=[1,2,3],)
    x = {
        "a": 1,
        "b": 2,
    }["a"]
    if a == {"a": 1,"b": 2,"c": 3,"d": 4,"e": 5,"f": 6,"g": 7,"h": 8,}["a"]:
        pass

def xxxxxxxxxxxxxxxxxxxxxxxxxxxx() -> Set[
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
]:
    json = {"k": {"k2": {"k3": [1,]}}}

def no_trailing_comma_one_argument_short(arg): pass
def no_trailing_comma_multiple_arguments_short(a, b, c): pass
def no_trailing_comma_one_argument_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
    some_argument
): pass
def no_trailing_comma_multiple_arguments_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
    first_arg, second_arg
): pass

# output

def f(
    a,
):
    d = {
        "key": "value",
    }
    tup = (1,)


def f2(
    a,
    b,
):
    d = {
        "key": "value",
        "key2": "value2",
    }
    tup = (
        1,
        2,
    )


def f(
    a: int = 1,
):
    call(
        arg={
            "explode": "this",
        }
    )
    call2(
        arg=[1, 2, 3],
    )
    x = {
        "a": 1,
        "b": 2,
    }["a"]
    if a == {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e": 5,
        "f": 6,
        "g": 7,
        "h": 8,
    }["a"]:
        pass


def xxxxxxxxxxxxxxxxxxxxxxxxxxxx() -> Set[
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
]:
    json = {
        "k": {
            "k2": {
                "k3": [
                    1,
                ]
            }
        }
    }


def no_trailing_comma_one_argument_short(arg):
    pass


def no_trailing_comma_multiple_arguments_short(a, b, c):
    pass


def no_trailing_comma_one_argument_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
    some_argument
):
    pass


def no_trailing_comma_multiple_arguments_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
    first_arg, second_arg
):
    pass
