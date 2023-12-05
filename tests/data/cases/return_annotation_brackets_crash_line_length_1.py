# flags: --preview --minimum-version=3.10 --line-length=1

def foo() -> tuple[int, int,]:
    ...
# output
def foo() -> tuple[
    int,
    int,
]: ...
