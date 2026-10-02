# flags: --minimum-version=3.12
# A `# fmt: skip` on a one-line compound statement with PEP 695 type parameters
# used to crash: the skipped leaves were converted but their emptied type
# parameter nodes stayed in the tree.
def f[T](): pass  # fmt: skip


def g[*Ts](): pass  # fmt: skip


def h[**P](): pass  # fmt: skip


def i[T: int, *Ts, **P](): pass  # fmt: skip


async def j[T](): pass  # fmt: skip


class C[T]: pass  # fmt: skip


class D[T](Base): pass  # fmt: skip


class A:
    def m[T](self): pass  # fmt: skip
