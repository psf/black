# flags: --minimum-version=3.10
match "test":
    case "test" if "first long condition" != "some loooooooooooooooooooooooooooooooooooooog condition":
        print("Test")

match match:
    case "test" if case != "not very loooooooooooooog condition":
        print("No format change")

match "test":
    case "test" if "any long condition" != "another long condition" and "this is a long condition":
        print("Test")

match "test":
    case "test" if "any long condition" != "another long condition" and "this is a looooong condition":
        print("Test")

# case black_test_patma_052 (originally in the pattern_matching_complex test case)
match x:
    case [1, 0] if x := x[:0]:
        y = 1
    case [1, 0] if (x := x[:0]):
        y = 1

# output

match "test":
    case "test" if (
        "first long condition"
        != "some loooooooooooooooooooooooooooooooooooooog condition"
    ):
        print("Test")

match match:
    case "test" if case != "not very loooooooooooooog condition":
        print("No format change")

match "test":
    case "test" if (
        "any long condition" != "another long condition" and "this is a long condition"
    ):
        print("Test")

match "test":
    case "test" if (
        "any long condition" != "another long condition"
        and "this is a looooong condition"
    ):
        print("Test")

# case black_test_patma_052 (originally in the pattern_matching_complex test case)
match x:
    case [1, 0] if x := x[:0]:
        y = 1
    case [1, 0] if x := x[:0]:
        y = 1
