class Body(model.BaseBody[
    "Keyword", "For", "While", "Group", "If", "Try", "Var", "Return", "Continue",
    "Break", "model.Message", "Error"
]):  # fmt: skip
    __slots__ = ()


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
