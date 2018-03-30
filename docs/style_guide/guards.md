## Use code block guards to skip reformat

To prevent *Black* from reformatting a certain code block, use the code block
guards, `# fmt: off` and `# fmt: on`, to surround the block.

### Original

```py3
def spaces_types(a: int = 1, b: tuple = (), c: list = [], d: dict = {}, e: bool = True, f: int = -1, g: int = 1 if False else 2, h: str = "", i: str = r''): ...

def example(session):
    # fmt: off
    result = session\
        .query(models.Customer.id)\
        .filter(models.Customer.account_id == account_id,
                models.Customer.email == email_address)\
        .order_by(models.Customer.id.asc())\
        .all()
    # fmt: on
```

### After *Black*

Notice: `space_types` changed, but `example` content was skipped
during reformatting.

```py3
def spaces_types(
    a: int = 1,
    b: tuple = (),
    c: list = [],
    d: dict = {},
    e: bool = True,
    f: int = -1,
    g: int = 1 if False else 2,
    h: str = "",
    i: str = r'',
):
    ...


def example(session):
    # fmt: off
    result = session\
        .query(models.Customer.id)\
        .filter(models.Customer.account_id == account_id,
                models.Customer.email == email_address)\
        .order_by(models.Customer.id.asc())\
        .all()
    # fmt: on
```

Similarly, *Black* recognizes [YAPF](https://github.com/google/yapf)'s block 
comments to the same effect, as a courtesy for straddling code.
