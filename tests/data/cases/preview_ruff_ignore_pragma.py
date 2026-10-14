# flags: --preview
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = 5  # ruff:ignore[bweh]
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx = 5  # ruff: ignore[E501]
yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy = "long"  # ruff:ignore


def f(action):
    if isinstance(action, argparse._SubParsersAction):  # ruff:ignore[private-member-access]
        pass
