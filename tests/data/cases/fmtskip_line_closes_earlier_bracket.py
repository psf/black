# The `# fmt: skip` line closes a bracket opened on an earlier line and opens one
# closed on a later line, so the whole statement is kept as it is.
def f(
    a,
) -> A[B  # fmt: skip
]:
    pass


class C:
    def method(
        self,
    ) -> dict[str,  # fmt: skip
        int]:
        pass


async def g(
    a,
) -> Union[List[int], float, str, bytes, Tuple[int]  # fmt: skip
]:
    pass

# output

# The `# fmt: skip` line closes a bracket opened on an earlier line and opens one
# closed on a later line, so the whole statement is kept as it is.
def f(
    a,
) -> A[B  # fmt: skip
]:
    pass


class C:
    def method(
        self,
    ) -> dict[str,  # fmt: skip
        int]:
        pass


async def g(
    a,
) -> Union[List[int], float, str, bytes, Tuple[int]  # fmt: skip
]:
    pass
