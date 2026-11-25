# flags: --preview
func(
    {
        "a": 37,
        "b": 42,
        "c": 927,
    }
)
func(
    [
        1,
        2,
    ]
)
func(
    [
        1,
        2,
    ],
)
func([1, 2])


# output
func({
    "a": 37,
    "b": 42,
    "c": 927,
})
func([
    1,
    2,
])
func(
    [
        1,
        2,
    ],
)
func([1, 2])
