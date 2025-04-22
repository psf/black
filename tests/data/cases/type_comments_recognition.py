# Issue #2097

# Variable assignment case (misformatted type comment)
perfectly_fine_variable = get_value() #    type: MyValue

# A standard one for comparison (misformatted spacing)
another_variable = get_another()      # type: AnotherValue

# Regular comment for comparison
regular_var = 10# A regular comment


# Function definition case
def process_data(
    user_data, #    type: UserDict
    session_id # type: SessionID
):
    # Function body starts here
    ...


# Another misformatted type comment
short_var = 1 #    type: int

# output
# Issue #2097

# Variable assignment case (misformatted type comment)
perfectly_fine_variable = get_value()  #    type: MyValue

# A standard one for comparison (misformatted spacing)
another_variable = get_another()  # type: AnotherValue

# Regular comment for comparison
regular_var = 10  # A regular comment


# Function definition case
def process_data(
    user_data,  #    type: UserDict
    session_id,  # type: SessionID
):
    # Function body starts here
    ...


# Another misformatted type comment
short_var = 1  #    type: int