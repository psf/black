if (
    True
    # sdf
):
    print("hw")

if ((
    True
    # sdf
)):
    print("hw")

if ((
    # type: ignore
    True
)):
    print("hw")

if ((
    True
    # type: ignore
)):
    print("hw")

if (
    # a long comment about
    # the condition below
    (a or b)
):
    pass

def return_true():
    return (
        (
            True  # this comment gets removed accidentally
        )
    )

def return_true():
    return (True)  # this comment gets removed accidentally


if (
    # huh comment
    (True)
):
    ...

if (
    # huh
    (
        # comment
        True
    )
):
    ...


# output

if (
    True
    # sdf
):
    print("hw")

if (
    True
    # sdf
):
    print("hw")

if (
    # type: ignore
    True
):
    print("hw")

if (
    True
    # type: ignore
):
    print("hw")

if (
    # a long comment about
    # the condition below
    a
    or b
):
    pass


def return_true():
    return True  # this comment gets removed accidentally


def return_true():
    return True  # this comment gets removed accidentally


if (
    # huh comment
    True
):
    ...

if (
    # huh
    # comment
    True
):
    ...
