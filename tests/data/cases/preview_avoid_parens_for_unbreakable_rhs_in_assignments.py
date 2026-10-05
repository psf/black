# flags: --preview

# Unbreakable strings exceeding line limit should not get wrapped in parens
# for annotated assignments, matching unannotated assignment behavior.
class A:
    attr1: str = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
    attr2 = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
    a[0] = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
    attr3: list[str] = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"


# Unbreakable long identifiers exceeding line length should also not get wrapped.
attr4: int = VERY_LONG_UNBREAKABLE_IDENTIFIER_THAT_EXCEEDS_LINE_LENGTH_AND_CANNOT_BE_SPLIT_BY_ANY_MEANS

# A long assignment whose string fits on the indented line should still be wrapped.
attr5: str = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Splittable expressions on the RHS should still be wrapped and split.
attr6: str = (
    "short" + "short" + "short" + "short" + "short" + "short" + "short" + "short" + "short"
)

# Unnecessary parentheses around an unbreakable string should be stripped.
attr7: str = (
    "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
)

# output

# Unbreakable strings exceeding line limit should not get wrapped in parens
# for annotated assignments, matching unannotated assignment behavior.
class A:
    attr1: str = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
    attr2 = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
    a[0] = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
    attr3: list[str] = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"


# Unbreakable long identifiers exceeding line length should also not get wrapped.
attr4: int = VERY_LONG_UNBREAKABLE_IDENTIFIER_THAT_EXCEEDS_LINE_LENGTH_AND_CANNOT_BE_SPLIT_BY_ANY_MEANS

# A long assignment whose string fits on the indented line should still be wrapped.
attr5: str = (
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)

# Splittable expressions on the RHS should still be wrapped and split.
attr6: str = (
    "short"
    + "short"
    + "short"
    + "short"
    + "short"
    + "short"
    + "short"
    + "short"
    + "short"
)

# Unnecessary parentheses around an unbreakable string should be stripped.
attr7: str = "this_is_very_very_long_this_is_very_very_long_this_is_very_very_long_this_is_very_very_long"
