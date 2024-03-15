# flags: --preview --minimum-version=3.10
match match:
    case "test" if case != "not very loooooooooooooog condition":  # comment
        pass

match smth:
    case "test" if "any long condition" != "another long condition" and "this is a long condition":
        pass
    case test if "any long condition" != "another long condition" and "this is a looooong condition":
        pass
    case test if "any long condition" != "another long condition" and "this is a looooong condition":  # some additional comments
        pass
    case test if (True): # some comment
        pass
    case test if (False
        ): # some comment
        pass
    case test if (True  # some comment
        ):
        pass  # some comment
    case cases if (True  # some comment
                   ): # some other comment
        pass  # some comment
    case match if (True  # some comment
                   ):
        pass  # some comment

# case black_test_patma_052 (originally in the pattern_matching_complex test case)
match x:
    case [1, 0] if x := x[:0]:
        y = 1
    case [1, 0] if (x := x[:0]):
        y = 1

# output

match match:
    case "test" if case != "not very loooooooooooooog condition":  # comment
        pass

match smth:
    case "test" if (
        "any long condition" != "another long condition" and "this is a long condition"
    ):
        pass
    case test if (
        "any long condition" != "another long condition"
        and "this is a looooong condition"
    ):
        pass
    case test if (
        "any long condition" != "another long condition"
        and "this is a looooong condition"
    ):  # some additional comments
        pass
    case test if True:  # some comment
        pass
    case test if False:  # some comment
        pass
    case test if True:  # some comment
        pass  # some comment
    case cases if True:  # some comment  # some other comment
        pass  # some comment
    case match if True:  # some comment
        pass  # some comment

# case black_test_patma_052 (originally in the pattern_matching_complex test case)
match x:
    case [1, 0] if x := x[:0]:
        y = 1
    case [1, 0] if x := x[:0]:
        y = 1
