# flags: --preview --no-preview-line-length-1
# split out from preview_hug_parens_with_brackes_and_square_brackets, as it produces
# different code on the second pass with line-length 1 in many cases.
# Seems to be about whether the last string in a sequence gets wrapped in parens or not.
foo(*["long long long long long line", "long long long long long line", "long long long long long line"])
func({"short line"})
func({"long line", "long long line", "long long long line", "long long long long line", "long long long long long line"})
func({{"long line", "long long line", "long long long line", "long long long long line", "long long long long long line"}})
func(("long line", "long long line", "long long long line", "long long long long line", "long long long long long line"))
func((("long line", "long long line", "long long long line", "long long long long line", "long long long long long line")))
func([["long line", "long long line", "long long long line", "long long long long line", "long long long long long line"]])


# Do not hug if the argument fits on a single line.
func({"fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"})
func(("fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"))
func(["fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"])
func(**{"fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit---"})
func(*("fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit----"))
array = [{"fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"}]
array = [("fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line")]
array = [["fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"]]

nested_array = [[["long line", "long long line", "long long long line", "long long long long line", "long long long long long line"]]]

# output

# split out from preview_hug_parens_with_brackes_and_square_brackets, as it produces
# different code on the second pass with line-length 1 in many cases.
# Seems to be about whether the last string in a sequence gets wrapped in parens or not.
foo(*[
    "long long long long long line",
    "long long long long long line",
    "long long long long long line",
])
func({"short line"})
func({
    "long line",
    "long long line",
    "long long long line",
    "long long long long line",
    "long long long long long line",
})
func({{
    "long line",
    "long long line",
    "long long long line",
    "long long long long line",
    "long long long long long line",
}})
func((
    "long line",
    "long long line",
    "long long long line",
    "long long long long line",
    "long long long long long line",
))
func(((
    "long line",
    "long long line",
    "long long long line",
    "long long long long line",
    "long long long long long line",
)))
func([[
    "long line",
    "long long line",
    "long long long line",
    "long long long long line",
    "long long long long long line",
]])


# Do not hug if the argument fits on a single line.
func(
    {"fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"}
)
func(
    ("fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line")
)
func(
    ["fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"]
)
func(
    **{"fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit---"}
)
func(
    *("fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit----")
)
array = [
    {"fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"}
]
array = [
    ("fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line")
]
array = [
    ["fit line", "fit line", "fit line", "fit line", "fit line", "fit line", "fit line"]
]

nested_array = [[[
    "long line",
    "long long line",
    "long long long line",
    "long long long long line",
    "long long long long long line",
]]]
