# Control
def double(a: int) -> int:
    return 2*a

# Remove the brackets
def double(a: int) -> (int):
    return 2*a

# Some newline variations
def double(a: int) -> (
    int):
    return 2*a

def double(a: int) -> (int
):
    return 2*a

def double(a: int) -> (
    int
):
    return 2*a

# Don't lose the comments
def double(a: int) -> ( # Hello
    int
):
    return 2*a

def double(a: int) -> (
    int # Hello
):
    return 2*a

# Really long annotations
def foo() -> (
    intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
):
    return 2

def foo() -> intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds:
    return 2

def foo() -> intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds | intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds:
    return 2

def foo(a: int, b: int, c: int,) -> intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds:
    return 2

def foo(a: int, b: int, c: int,) -> intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds | intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds:
    return 2

# Split args but no need to split return
def foo(a: int, b: int, c: int,) -> int:
    return 2

# output
# Control
def double(a: int) -> int:
    return 2 * a


# Remove the brackets
def double(a: int) -> int:
    return 2 * a


# Some newline variations
def double(a: int) -> int:
    return 2 * a


def double(a: int) -> int:
    return 2 * a


def double(a: int) -> int:
    return 2 * a


# Don't lose the comments
def double(a: int) -> int:  # Hello
    return 2 * a


def double(a: int) -> int:  # Hello
    return 2 * a


# Really long annotations
def foo() -> (
    intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
):
    return 2


def foo() -> (
    intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
):
    return 2


def foo() -> (
    intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
    | intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
):
    return 2


def foo(
    a: int,
    b: int,
    c: int,
) -> intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds:
    return 2


def foo(
    a: int,
    b: int,
    c: int,
) -> (
    intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
    | intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
):
    return 2


# Split args but no need to split return
def foo(
    a: int,
    b: int,
    c: int,
) -> int:
    return 2
