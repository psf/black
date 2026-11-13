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

# A tuple target written without parentheses gets invisible ones, so a split tuple
# target keeps its parentheses as invisible ones to split the same way.
if x:
    (self._cls_dict["__getstate__"],
     self._cls_dict["__setstate__"]) = self._make_getstate_setstate()

# A comment before the statement does not stop the drop of the target's invisible
# parentheses, so the split must match the one written without parentheses.
def restore_region_with_comment(surface, region, sly, slx, sh, sw):
    # The standalone comment is kept.
    (np.frombuffer(surface.get_data(), np.uint32)
     .reshape((sh, sw))[sly, slx]) = region._data

# Blank lines around the comment do not change that.
def restore_region_with_blank_lines(surface, region, sly, slx, sh, sw):

    # The standalone comment is kept.

    (np.frombuffer(surface.get_data(), np.uint32)
     .reshape((sh, sw))[sly, slx]) = region._data

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

# A tuple target written without parentheses gets invisible ones, so a split tuple
# target keeps its parentheses as invisible ones to split the same way.
if x:
    self._cls_dict["__getstate__"], self._cls_dict["__setstate__"] = (
        self._make_getstate_setstate()
    )


# A comment before the statement does not stop the drop of the target's invisible
# parentheses, so the split must match the one written without parentheses.
def restore_region_with_comment(surface, region, sly, slx, sh, sw):
    # The standalone comment is kept.
    np.frombuffer(surface.get_data(), np.uint32).reshape((sh, sw))[
        sly, slx
    ] = region._data


# Blank lines around the comment do not change that.
def restore_region_with_blank_lines(surface, region, sly, slx, sh, sw):

    # The standalone comment is kept.

    np.frombuffer(surface.get_data(), np.uint32).reshape((sh, sw))[
        sly, slx
    ] = region._data
