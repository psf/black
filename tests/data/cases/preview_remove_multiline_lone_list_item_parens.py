# flags: --unstable
items  = [(x for x in [1])]

items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    )
]
items = [
    (
        {"key1": "val1", "key2": "val2"}
        if some_var == ""
        else {"key": "val"}
    )
]
items = [
    (
        "123456890123457890123468901234567890"
        if some_var == "long strings"
        else "123467890123467890"
    )
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        and some_var == "long strings"
        and {"key": "val"}
    )
]
items = [
    (
        "123456890123457890123468901234567890"
        and some_var == "long strings"
        and "123467890123467890"
    )
]
items = [
    (
        long_variable_name
        and even_longer_variable_name
        and yet_another_very_long_variable_name
    )
]

# Shouldn't remove trailing commas
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    ),
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        and some_var == "long strings"
        and {"key": "val"}
    ),
]
items = [
    (
        "123456890123457890123468901234567890"
        and some_var == "long strings"
        and "123467890123467890"
    ),
]
items = [
    (
        long_variable_name
        and even_longer_variable_name
        and yet_another_very_long_variable_name
    ),
]

# Shouldn't add parentheses
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]
items = [{"key1": "val1", "key2": "val2"} if some_var == "" else {"key": "val"}]

# Shouldn't crash with comments
items = [
    (  # comment
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    )
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    )  # comment
]

items = [  # comment
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    )
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    )
]  # comment

items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}  # comment
        if some_var == "long strings"
        else {"key": "val"}
    )
]

items = [  # comment
    (  # comment
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    )
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    )  # comment
]  # comment


# output
items = [(x for x in [1])]

items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]
items = [{"key1": "val1", "key2": "val2"} if some_var == "" else {"key": "val"}]
items = [
    "123456890123457890123468901234567890"
    if some_var == "long strings"
    else "123467890123467890"
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    and some_var == "long strings"
    and {"key": "val"}
]
items = [
    "123456890123457890123468901234567890"
    and some_var == "long strings"
    and "123467890123467890"
]
items = [
    long_variable_name
    and even_longer_variable_name
    and yet_another_very_long_variable_name
]

# Shouldn't remove trailing commas
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        if some_var == "long strings"
        else {"key": "val"}
    ),
]
items = [
    (
        {"key1": "val1", "key2": "val2", "key3": "val3"}
        and some_var == "long strings"
        and {"key": "val"}
    ),
]
items = [
    (
        "123456890123457890123468901234567890"
        and some_var == "long strings"
        and "123467890123467890"
    ),
]
items = [
    (
        long_variable_name
        and even_longer_variable_name
        and yet_another_very_long_variable_name
    ),
]

# Shouldn't add parentheses
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]
items = [{"key1": "val1", "key2": "val2"} if some_var == "" else {"key": "val"}]

# Shouldn't crash with comments
items = [  # comment
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]  # comment

items = [  # comment
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]  # comment

items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}  # comment
    if some_var == "long strings"
    else {"key": "val"}
]

items = [  # comment  # comment
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]
items = [
    {"key1": "val1", "key2": "val2", "key3": "val3"}
    if some_var == "long strings"
    else {"key": "val"}
]  # comment  # comment
