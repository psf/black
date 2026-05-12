class Body(model.BaseBody[
    "Keyword", "For", "While", "Group", "If", "Try", "Var", "Return", "Continue",
    "Break", "model.Message", "Error"
]):  # fmt: skip
    __slots__ = ()


class Foo(Base[\
    "A", "B"\
]):  # fmt: skip

    def a(self): ...


def make_result(
    first  : int,
    second:   str,
):  # fmt: skip
    return first, second


async def fetch_result(
    client,
    *,
    timeout  =   1,
):  # fmt: skip
    return await client.fetch(timeout=timeout)


if (
    has_permission(  user  )
    and is_ready(  item  )
):  # fmt: skip
    process(item)

match (method, *path.split("/")):
    case ("GET", "parent", _, "resource", resource_id) \
            | ("GET", "resource", resource_id):  # fmt: skip
        pass
    case _:
        pass

match x:
    case a \
        | b \
        | c:  # fmt: skip
        pass
