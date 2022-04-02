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
def double() -> (
    intsdfsafafafdfdsasdfsfsdfasdfafdsafdfdsfasdskdsdsfdsafdsafsdfdasfffsfdsfdsafafhdskfhdsfjdslkfdlfsdkjhsdfjkdshfkljds
):
    return 2
