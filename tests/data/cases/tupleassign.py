# This is a standalone comment.
sdfjklsdfsjldkflkjsf, sdfjsdfjlksdljkfsdlkf, sdfsdjfklsdfjlksdljkf, sdsfsdfjskdflsfsdf = 1, 2, 3

# This is as well.
this_will_be_wrapped_in_parens, = struct.unpack(b"12345678901234567890")

(a,) = call()

# output


# This is a standalone comment.
(
    sdfjklsdfsjldkflkjsf,
    sdfjsdfjlksdljkfsdlkf,
    sdfsdjfklsdfjlksdljkf,
    sdsfsdfjskdflsfsdf,
) = (1, 2, 3)

# This is as well.
(this_will_be_wrapped_in_parens,) = struct.unpack(b"12345678901234567890")

(a,) = call()