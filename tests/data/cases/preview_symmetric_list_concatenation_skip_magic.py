# flags: --preview --skip-magic-trailing-comma

# Ignored trailing commas do not prevent symmetric formatting.
values = [
    "first_long_value",
    "second_long_value",
] + ["third_long_value", "fourth_long_value"]

# output

# Ignored trailing commas do not prevent symmetric formatting.
values = (
    ["first_long_value", "second_long_value"]
    + ["third_long_value", "fourth_long_value"]
)
