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