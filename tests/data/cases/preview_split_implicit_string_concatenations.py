# flags: --preview

ValueError(f"Invalid input:\n * x={x}\n * y={y}\n * z={z}")
f(f"Data: {foo: <4} | {bar:8d} | {qux: >16}")
f(f"Data: {foo: <4} | {bar:8d} | {qux: >16}")
f(f"Data: {foo: <4} | {bar:8d} | {qux: >16}")
f(f"Data: {foo: <4} | ")
f("aaabbb", "ccc")
f(
    "aaabbb",
)
f("Data: ")
items = ["ab"]
f(g("aabb"))
x = "ab"
d = {"key": "xy"}
f("Data: here")
f("aaabbb")  # comment
f(
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    "cccccccccccccccccccccccccccccccccccccccc"
)

# output

ValueError(f"Invalid input:\n * x={x}\n * y={y}\n * z={z}")
f(f"Data: {foo: <4} | {bar:8d} | {qux: >16}")
f(f"Data: {foo: <4} | {bar:8d} | {qux: >16}")
f(f"Data: {foo: <4} | {bar:8d} | {qux: >16}")
f(f"Data: {foo: <4} | ")
f("aaabbb", "ccc")
f(
    "aaabbb",
)
f("Data: ")
items = ["ab"]
f(g("aabb"))
x = "ab"
d = {"key": "xy"}
f("Data: here")
f("aaabbb")  # comment
f(
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    "cccccccccccccccccccccccccccccccccccccccc"
)
