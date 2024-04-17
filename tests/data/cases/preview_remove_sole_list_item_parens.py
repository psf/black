# flags: --unstable
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "longstring"
        else { "key": "val" }
    )
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "longstring"
        else { "key": "val" }
    ),
]
items = [(
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "longstring"
    else { "key": "val" }
)]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "longstring"
    else {"key": "val"}
]
items = [
    (
        {"key1": "val1", "key2": "val2"} if some_var == "longstring" else { "key": "val" }
    )
]
items = [(
    {"key1": "val1", "key2": "val2"} if some_var == "" else { "key": "val" }
)]
items = [
    {"key1": "val1", "key2": "val2"} if some_var == "longstring" else { "key": "val" }
]
items = [
    ({"key1": "val1", "key2": "val2"} if some_var == "longstring" else { "key": "val" })
]
items = [({"key1": "val1", "key2": "val2"} if some_var == "" else { "key": "val" })]
items = [{"key1": "val1", "key2": "val2"} if some_var == "" else { "key": "val" }]

items = [
    (
        "123456890123457890123468901234567890"
        if some_var == "longstrings"
        else "123467890123467890"
    )
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    and some_var == "longstring"
    and {"key": "val"}
]
items = [
    (
        "123456890123457890123468901234567890"
        and some_var == "longstrings"
        and "123467890123467890"
    )
]
items = [(
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    and some_var == "longstring"
    and {"key": "val"}
)]


items = [
    (
        long_variable_name
        and even_longer_variable_name
        and yet_another_very_long_variable_name
    )
]

items = [
    (
        long_variable_name
        and even_longer_variable_name
        and yet_another_very_long_variable_name
    ),
]


# output
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "longstring"
    else {"key": "val"}
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "longstring"
        else {"key": "val"}
    ),
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "longstring"
    else {"key": "val"}
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "longstring"
    else {"key": "val"}
]
items = [
    {"key1": "val1", "key2": "val2"} if some_var == "longstring" else {"key": "val"}
]
items = [{"key1": "val1", "key2": "val2"} if some_var == "" else {"key": "val"}]
items = [
    {"key1": "val1", "key2": "val2"} if some_var == "longstring" else {"key": "val"}
]
items = [
    {"key1": "val1", "key2": "val2"} if some_var == "longstring" else {"key": "val"}
]
items = [{"key1": "val1", "key2": "val2"} if some_var == "" else {"key": "val"}]
items = [{"key1": "val1", "key2": "val2"} if some_var == "" else {"key": "val"}]

items = [
    "123456890123457890123468901234567890"
    if some_var == "longstrings"
    else "123467890123467890"
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    and some_var == "longstring"
    and {"key": "val"}
]
items = [
    "123456890123457890123468901234567890"
    and some_var == "longstrings"
    and "123467890123467890"
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    and some_var == "longstring"
    and {"key": "val"}
]


items = [
    long_variable_name
    and even_longer_variable_name
    and yet_another_very_long_variable_name
]

items = [
    (
        long_variable_name
        and even_longer_variable_name
        and yet_another_very_long_variable_name
    ),
]
