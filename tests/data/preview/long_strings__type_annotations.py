def func(
    arg1,
    arg2,
) -> Set["this_is_a_very_long_module_name.AndAVeryLongClasName"
         ".WithAVeryVeryVeryVeryVeryLongSubClassName"]:
  pass


def func(
    argument: (
        "VeryLongClassNameWithAwkwardGenericSubtype[int] |"
        "VeryLongClassNameWithAwkwardGenericSubtype[str]"
    ),
) -> (
    "VeryLongClassNameWithAwkwardGenericSubtype[int] |"
    "VeryLongClassNameWithAwkwardGenericSubtype[str]"
):
  pass


def func(
    argument: (
        "int |"
        "str"
    ),
) -> Set["int |"
         " str"]:
  pass


# output


def func(
    arg1,
    arg2,
) -> Set[
    "this_is_a_very_long_module_name.AndAVeryLongClasName"
    ".WithAVeryVeryVeryVeryVeryLongSubClassName"
]:
    pass


def func(
    argument: (
        "VeryLongClassNameWithAwkwardGenericSubtype[int] |"
        "VeryLongClassNameWithAwkwardGenericSubtype[str]"
    ),
) -> (
    "VeryLongClassNameWithAwkwardGenericSubtype[int] |"
    "VeryLongClassNameWithAwkwardGenericSubtype[str]"
):
    pass


def func(
    argument: ("int |" "str"),
) -> Set["int |" " str"]:
    pass
