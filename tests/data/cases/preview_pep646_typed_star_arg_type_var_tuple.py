# flags: --minimum-version=3.11 --preview


def fn(*args: *tuple[*A, B]) -> None:
    pass


fn.__annotations__
