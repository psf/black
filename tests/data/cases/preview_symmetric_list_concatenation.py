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

# A body that fits inside optional parentheses keeps the existing bracket split.
values = [first_value, second_value, third_value] + [fourth_value, fifth_value, sixth_value]

# Chained concatenations already use the normal delimiter split.
chained = ["first_long_value", "second_long_value"] + ["third_long_value", "fourth_long_value"] + ["fifth_long_value", "sixth_long_value"]

# Mixed operands are not symmetric list concatenations.
mixed_left = ["first_long_value", "second_long_value", "third_long_value"] + tuple_with_a_very_long_name
mixed_right = list_with_a_very_long_name + ["first_long_value", "second_long_value", "third_long_value"]

# Short concatenations stay on one line.
small = [1, 2] + [3, 4]

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

# A body that fits inside optional parentheses keeps the existing bracket split.
values = [first_value, second_value, third_value] + [
    fourth_value,
    fifth_value,
    sixth_value,
]

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
