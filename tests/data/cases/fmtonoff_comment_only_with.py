# flags: --minimum-version=3.10

with open("bug.txt", "r", encoding="utf-8") as fh1:
    pass
# fmt: off
# fmt: on
# xxx
# fmt: off
# fmt: on
with open("bug.txt", "r", encoding="utf-8") as fh2:
    pass
def fn(str: str) -> float:
    match str:
        case _:
            pass

# output

with open("bug.txt", "r", encoding="utf-8") as fh1:
    pass
# fmt: off
# fmt: on

# xxx
# fmt: off
# fmt: on
with open("bug.txt", "r", encoding="utf-8") as fh2:
    pass


def fn(str: str) -> float:
    match str:
        case _:
            pass
