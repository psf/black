# flags: --minimum-version=3.12
x = f"result {
    value  # inline comment in interpolation
} done"


y = f"nested {f"inner {a}"} outer"


z = f"reuse {"double quotes inside"} works now"


spec = f"padded {value:{width}d} end"


conv = f"repr {obj!r} str {obj!s} ascii {obj!a}"


debug = f"debug {2 + 2 = } and {name = }"


multi = f"line one {
    first_value  # comment one
} middle {
    second_value  # comment two
} last"


call = function(f"prefix {some.method(argument_one, argument_two, argument_three)} suffix", other)


nested_spec = f"a{2 + 2:=^{foo(x + y**2):another spec}}b"


triple = f"""
    header {value  # comment
    } footer
"""

# output

x = f"result {
    value  # inline comment in interpolation
} done"


y = f"nested {f"inner {a}"} outer"


z = f"reuse {"double quotes inside"} works now"


spec = f"padded {value:{width}d} end"


conv = f"repr {obj!r} str {obj!s} ascii {obj!a}"


debug = f"debug {2 + 2 = } and {name = }"


multi = f"line one {
    first_value  # comment one
} middle {
    second_value  # comment two
} last"


call = function(
    f"prefix {some.method(argument_one, argument_two, argument_three)} suffix", other
)


nested_spec = f"a{2 + 2:=^{foo(x + y**2):another spec}}b"


triple = f"""
    header {value  # comment
    } footer
"""
