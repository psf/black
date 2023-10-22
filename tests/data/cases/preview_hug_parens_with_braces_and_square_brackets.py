# flags: --preview
def foo_brackets(request):
    return JsonResponse(
        {
            "var_1": foo,
            "var_2": bar,
        }
    )

def foo_square_brackets(request):
    return JsonResponse(
        [
            "var_1",
            "var_2",
        ]
    )

func({"a": 37, "b": 42, "c": 927, "aaaaaaaaaaaaaaaaaaaaaaaaa": 11111111111111111111111111111111111111111})

func(["random_string_number_one","random_string_number_two","random_string_number_three","random_string_number_four"])

func(
    {
        # expand me
        'a':37,
        'b':42,
        'c':927
    }
)

func(
    [
        'a',
        'b',
        'c',
    ]
)

# output
def foo_brackets(request):
    return JsonResponse({
        "var_1": foo,
        "var_2": bar,
    })


def foo_square_brackets(request):
    return JsonResponse([
        "var_1",
        "var_2",
    ])


func({
    "a": 37,
    "b": 42,
    "c": 927,
    "aaaaaaaaaaaaaaaaaaaaaaaaa": 11111111111111111111111111111111111111111,
})

func([
    "random_string_number_one",
    "random_string_number_two",
    "random_string_number_three",
    "random_string_number_four",
])

func({
    # expand me
    "a": 37,
    "b": 42,
    "c": 927,
})

func([
    "a",
    "b",
    "c",
])
