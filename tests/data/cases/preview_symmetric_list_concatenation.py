# flags: --preview

# Regression test for https://github.com/psf/black/issues/260.
search_fields = (["file__%s" % field for field in FileAdmin.search_fields] + ["resource__%s" % field for field in ResourceAdmin.search_fields])

# Plain list displays receive the same symmetric treatment.
names = ["Alice", "Bob", "Charlie", "Diana", "Edward"] + ["Fiona", "George", "Harriet", "Isabelle"]

# Comments on an operand stay attached and formatting remains stable.
commented = (
    ["first_long_value", "second_long_value", "third_long_value"]  # first list
    + ["fourth_long_value", "fifth_long_value", "sixth_long_value"]
)

commented_left = (
    ["first_value", "second_value", "third_value"]  # abc
    + ["fourth_value", "fifth_value", "sixth_value"]
)
commented_right = (
    ["first_value", "second_value", "third_value"]
    + ["fourth_value", "fifth_value", "sixth_value"]  # abc
)

# Split symmetrically even when the RHS alone fits inside optional parentheses.
values = [first_value, second_value, third_value] + [fourth_value, fifth_value, sixth_value]

# Chained concatenations already use the normal delimiter split.
chained = ["first_long_value", "second_long_value"] + ["third_long_value", "fourth_long_value"] + ["fifth_long_value", "sixth_long_value"]

# Mixed operands are not symmetric list concatenations.
mixed_left = ["first_long_value", "second_long_value", "third_long_value"] + tuple_with_a_very_long_name
mixed_right = list_with_a_very_long_name + ["first_long_value", "second_long_value", "third_long_value"]

# Short concatenations stay on one line.
small = [1, 2] + [3, 4]

# Lists that already require bracket splitting keep the existing formatting.
long_left = ["first_value_with_an_extremely_long_name", "second_value_with_an_extremely_long_name", "third"] + ["short"]
long_right = ["short"] + ["first_value_with_an_extremely_long_name", "second_value_with_an_extremely_long_name", "third"]
both_long = ["first_value_with_an_extremely_long_name", "second_value_with_an_extremely_long_name", "third"] + ["fourth_value_with_an_extremely_long_name", "fifth_value_with_an_extremely_long_name", "sixth"]

# Magic trailing commas also keep the existing formatting.
magic_left = [
    "first_long_value",
    "second_long_value",
] + ["third_long_value", "fourth_long_value"]
magic_right = ["first_long_value", "second_long_value"] + [
    "third_long_value",
    "fourth_long_value",
]

# output

# Regression test for https://github.com/psf/black/issues/260.
search_fields = (
    ["file__%s" % field for field in FileAdmin.search_fields]
    + ["resource__%s" % field for field in ResourceAdmin.search_fields]
)

# Plain list displays receive the same symmetric treatment.
names = (
    ["Alice", "Bob", "Charlie", "Diana", "Edward"]
    + ["Fiona", "George", "Harriet", "Isabelle"]
)

# Comments on an operand stay attached and formatting remains stable.
commented = (
    ["first_long_value", "second_long_value", "third_long_value"]  # first list
    + ["fourth_long_value", "fifth_long_value", "sixth_long_value"]
)

commented_left = (
    ["first_value", "second_value", "third_value"]  # abc
    + ["fourth_value", "fifth_value", "sixth_value"]
)
commented_right = (
    ["first_value", "second_value", "third_value"]
    + ["fourth_value", "fifth_value", "sixth_value"]  # abc
)

# Split symmetrically even when the RHS alone fits inside optional parentheses.
values = (
    [first_value, second_value, third_value]
    + [fourth_value, fifth_value, sixth_value]
)

# Chained concatenations already use the normal delimiter split.
chained = (
    ["first_long_value", "second_long_value"]
    + ["third_long_value", "fourth_long_value"]
    + ["fifth_long_value", "sixth_long_value"]
)

# Mixed operands are not symmetric list concatenations.
mixed_left = [
    "first_long_value",
    "second_long_value",
    "third_long_value",
] + tuple_with_a_very_long_name
mixed_right = list_with_a_very_long_name + [
    "first_long_value",
    "second_long_value",
    "third_long_value",
]

# Short concatenations stay on one line.
small = [1, 2] + [3, 4]

# Lists that already require bracket splitting keep the existing formatting.
long_left = [
    "first_value_with_an_extremely_long_name",
    "second_value_with_an_extremely_long_name",
    "third",
] + ["short"]
long_right = ["short"] + [
    "first_value_with_an_extremely_long_name",
    "second_value_with_an_extremely_long_name",
    "third",
]
both_long = [
    "first_value_with_an_extremely_long_name",
    "second_value_with_an_extremely_long_name",
    "third",
] + [
    "fourth_value_with_an_extremely_long_name",
    "fifth_value_with_an_extremely_long_name",
    "sixth",
]

# Magic trailing commas also keep the existing formatting.
magic_left = [
    "first_long_value",
    "second_long_value",
] + ["third_long_value", "fourth_long_value"]
magic_right = ["first_long_value", "second_long_value"] + [
    "third_long_value",
    "fourth_long_value",
]
