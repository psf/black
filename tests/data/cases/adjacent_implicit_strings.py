# The main use case from issue #3955
# Adjacent strings in function call should be wrapped
def f(*args):
    pass


f(
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor"
    "incididunt ut labore et dolore magna aliqua Ut enim ad minim",
    "",
)

# output
def f(*args):
    pass


f(
    (
        "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor"
        "incididunt ut labore et dolore magna aliqua Ut enim ad minim"
    ),
    "",
)


# Adjacent strings in return statement
def get_message():
    return "hello" "world"

# output
def get_message():
    return ("hello" "world")