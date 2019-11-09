x = "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."

print("This is a really long string inside of a print statement with extra arguments attached at the end of it.", x, y, z)

print("This is a really long string inside of a print statement with no extra arguments attached at the end of it.")

D = {"The First": "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", "The Second": "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}

func_with_keywords(my_arg, my_kwarg="Long keyword strings also need to be wrapped, but they will probably need to be handled a little bit differently.")

x = "We also need to be sure to preserve any and all {} which may or may not be attached to the string in question.".format("method calls")

x = "While we are on the topic of %s, we should also note that old-style formatting must also be preserved, since some %s still uses it." % ("formatting", "code")

bad_split = (
    "But what should happen when code has already been formatted but in the wrong way?"
    " Like with a space at the beginning instead of the end."
    " Or what about when it is split too soon?"
)

bad_split = (
    "But what should happen when code has already "
    "been formatted but in the wrong way? Like "
    "with a space at the beginning instead of the "
    "end. Or what about when it is split too "
    "soon?"
)

fstring = f"f-strings definitely make things more {difficult} than they need to be for black. But boy they sure are handy. The problem is that some lines will need to have the 'f' whereas others do not. This {line}, for example, needs one."

# output

x = (
    "This is a really long string that can't possibly be expected to fit all together "
    "on one line. In fact it may even take up three or more lines... like four or "
    "five... but probably just three."
)

print(
    (
        "This is a really long string inside of a print statement with extra arguments "
        "attached at the end of it."
    ),
    x,
    y,
    z,
)

print(
    "This is a really long string inside of a print statement with no extra arguments "
    "attached at the end of it."
)

D = {
    "The First": (
        "This is a really long string that can't possibly be expected to fit all "
        "together on one line. Also it is inside a dictionary, so formatting is more "
        "difficult."
    ),
    "The Second": (
        "This is another really really (not really) long string that also can't be "
        "expected to fit on one line and is, like the other string, inside a "
        "dictionary."
    ),
}

func_with_keywords(
    my_arg,
    my_kwarg=(
        "Long keyword strings also need to be wrapped, but they will probably need to "
        "be handled a little bit differently."
    ),
)

x = (
    "We also need to be sure to preserve any and all {} which may or may not be "
    "attached to the string in question.".format("method calls")
)

x = (
    "While we are on the topic of %s, we should also note that old-style formatting "
    "must also be preserved, since some %s still uses it." % ("formatting", "code")
)

bad_split = (
    "But what should happen when code has already been formatted but in the wrong way? "
    "Like with a space at the beginning instead of the end. Or what about when it is "
    "split too soon?"
)

bad_split = (
    "But what should happen when code has already been formatted but in the wrong way? "
    "Like with a space at the beginning instead of the end. Or what about when it is "
    "split too soon?"
)

fstring = (
    f"f-strings definitely make things more {difficult} than they need to be for "
    "black. But boy they sure are handy. The problem is that some lines will need to "
    f"have the 'f' whereas others do not. This {line}, for example, needs one."
)
