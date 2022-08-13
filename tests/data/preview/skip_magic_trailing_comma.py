# We should not remove the trailing comma in a single-element subscript.
a: tuple[int,]
b = tuple[int,]

# But commas in multiple element subscripts should be removed.
c: tuple[int, int,]
d = tuple[int, int,]

# Remove commas for non-subscripts.
small_list = [1,]
list_of_types = [tuple[int,],]
small_set = {1,}
set_of_types = {tuple[int,],}

# Except single element tuples
small_tuple = (1,)

# output
# We should not remove the trailing comma in a single-element subscript.
a: tuple[int,]
b = tuple[int,]

# But commas in multiple element subscripts should be removed.
c: tuple[int, int]
d = tuple[int, int]

# Remove commas for non-subscripts.
small_list = [1]
list_of_types = [tuple[int,]]
small_set = {1}
set_of_types = {tuple[int,]}

# Except single element tuples
small_tuple = (1,)
