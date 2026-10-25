# Remove unnecessary parentheses from LHS of assignments


def a():
    return [1, 2, 3]


# Single variable with unnecessary parentheses
(b) = a()[0]

# Tuple unpacking with unnecessary parentheses
(c, *_) = a()

# These should not be changed - parentheses are necessary
(d,) = a()  # single-element tuple
e = (1 + 2) * 3  # RHS has precedence needs


# A target split over lines keeps its parentheses until the next pass, which must
# still split the line the same way once they are gone.
def restore_region(surface, region, sly, slx, sh, sw):
    (np.frombuffer(surface.get_data(), np.uint32)
     .reshape((sh, sw))[sly, slx]) = region._data

# The blank lines before the statement stay, and a comment inside the parentheses is kept.
x = 1


(a.b) = 1
(a.b  # c
) = 1

# output

# Remove unnecessary parentheses from LHS of assignments


def a():
    return [1, 2, 3]


# Single variable with unnecessary parentheses
b = a()[0]

# Tuple unpacking with unnecessary parentheses
c, *_ = a()

# These should not be changed - parentheses are necessary
(d,) = a()  # single-element tuple
e = (1 + 2) * 3  # RHS has precedence needs


# A target split over lines keeps its parentheses until the next pass, which must
# still split the line the same way once they are gone.
def restore_region(surface, region, sly, slx, sh, sw):
    np.frombuffer(surface.get_data(), np.uint32).reshape((sh, sw))[
        sly, slx
    ] = region._data


# The blank lines before the statement stay, and a comment inside the parentheses is kept.
x = 1


a.b = 1
a.b = 1  # c
