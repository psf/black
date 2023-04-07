x = "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."

x += "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."

y = (
    'Short string'
)

print('This is a really long string inside of a print statement with extra arguments attached at the end of it.', x, y, z)

print("This is a really long string inside of a print statement with no extra arguments attached at the end of it.")

D1 = {"The First": "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", "The Second": "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}

D2 = {1.0: "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", 2.0: "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}

D3 = {x: "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", y: "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}

D4 = {"A long and ridiculous {}".format(string_key): "This is a really really really long string that has to go i,side of a dictionary. It is soooo bad.", some_func("calling", "some", "stuff"): "This is a really really really long string that has to go inside of a dictionary. It is {soooo} bad (#{x}).".format(sooo="soooo", x=2), "A %s %s" % ("formatted", "string"): "This is a really really really long string that has to go inside of a dictionary. It is %s bad (#%d)." % ("soooo", 2)}

D5 = {  # Test for https://github.com/psf/black/issues/3261
    ("This is a really long string that can't be expected to fit in one line and is used as a nested dict's key"): {"inner": "value"},
}

D6 = {  # Test for https://github.com/psf/black/issues/3261
    ("This is a really long string that can't be expected to fit in one line and is used as a dict's key"): ["value1", "value2"],
}

L1 = ["The is a short string", "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a list literal, so it's expected to be wrapped in parens when splitting to avoid implicit str concatenation.", short_call("arg", {"key": "value"}), "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a list literal.", ("parens should be stripped for short string in list")]

L2 = ["This is a really long string that can't be expected to fit in one line and is the only child of a list literal."]

S1 = {"The is a short string", "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a set literal, so it's expected to be wrapped in parens when splitting to avoid implicit str concatenation.", short_call("arg", {"key": "value"}), "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a set literal.", ("parens should be stripped for short string in set")}

S2 = {"This is a really long string that can't be expected to fit in one line and is the only child of a set literal."}

T1 = ("The is a short string", "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a tuple literal, so it's expected to be wrapped in parens when splitting to avoid implicit str concatenation.", short_call("arg", {"key": "value"}), "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a tuple literal.", ("parens should be stripped for short string in list"))

T2 = ("This is a really long string that can't be expected to fit in one line and is the only child of a tuple literal.",)

func_with_keywords(my_arg, my_kwarg="Long keyword strings also need to be wrapped, but they will probably need to be handled a little bit differently.")

bad_split1 = (
    'But what should happen when code has already been formatted but in the wrong way? Like'
    " with a space at the end instead of the beginning. Or what about when it is split too soon?"
)

bad_split2 = "But what should happen when code has already " \
             "been formatted but in the wrong way? Like " \
             "with a space at the end instead of the " \
             "beginning. Or what about when it is split too " \
             "soon? In the case of a split that is too " \
             "short, black will try to honer the custom " \
             "split."

bad_split3 = (
    "What if we have inline comments on "  # First Comment
    "each line of a bad split? In that "  # Second Comment
    "case, we should just leave it alone."  # Third Comment
)

bad_split_func1(
    "But what should happen when code has already "
    "been formatted but in the wrong way? Like "
    "with a space at the end instead of the "
    "beginning. Or what about when it is split too "
    "soon? In the case of a split that is too "
    "short, black will try to honer the custom "
    "split.",
    xxx, yyy, zzz
)

bad_split_func2(
    xxx, yyy, zzz,
    long_string_kwarg="But what should happen when code has already been formatted but in the wrong way? Like "
                      "with a space at the end instead of the beginning. Or what about when it is split too "
                      "soon?",
)

bad_split_func3(
    (
        "But what should happen when code has already "
        r"been formatted but in the wrong way? Like "
        "with a space at the end instead of the "
        r"beginning. Or what about when it is split too "
        r"soon? In the case of a split that is too "
        "short, black will try to honer the custom "
        "split."
    ),
    xxx,
    yyy,
    zzz,
)

inline_comments_func1(
    "if there are inline "
    "comments in the middle "
    # Here is the standard alone comment.
    "of the implicitly concatenated "
    "string, we should handle "
    "them correctly",
    xxx,
)

inline_comments_func2(
    "what if the string is very very very very very very very very very very long and this part does "
    "not fit into a single line? "
    # Here is the standard alone comment.
    "then the string should still be properly handled by merging and splitting "
    "it into parts that fit in line length.",
    xxx,
)

raw_string = r"This is a long raw string. When re-formatting this string, black needs to make sure it prepends the 'r' onto the new string."

fmt_string1 = "We also need to be sure to preserve any and all {} which may or may not be attached to the string in question.".format("method calls")

fmt_string2 = "But what about when the string is {} but {}".format("short", "the method call is really really really really really really really really long?")

old_fmt_string1 = "While we are on the topic of %s, we should also note that old-style formatting must also be preserved, since some %s still uses it." % ("formatting", "code")

old_fmt_string2 = "This is a %s %s %s %s" % ("really really really really really", "old", "way to format strings!", "Use f-strings instead!")

old_fmt_string3 = "Whereas only the strings after the percent sign were long in the last example, this example uses a long initial string as well. This is another %s %s %s %s" % ("really really really really really", "old", "way to format strings!", "Use f-strings instead!")

fstring = f"f-strings definitely make things more {difficult} than they need to be for {{black}}. But boy they sure are handy. The problem is that some lines will need to have the 'f' whereas others do not. This {line}, for example, needs one."

fstring_with_no_fexprs = f"Some regular string that needs to get split certainly but is NOT an fstring by any means whatsoever."

comment_string = "Long lines with inline comments should have their comments appended to the reformatted string's enclosing right parentheses."  # This comment gets thrown to the top.

arg_comment_string = print("Long lines with inline comments which are apart of (and not the only member of) an argument list should have their comments appended to the reformatted string's enclosing left parentheses.",  # This comment gets thrown to the top.
    "Arg #2", "Arg #3", "Arg #4", "Arg #5")

pragma_comment_string1 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa: E501

pragma_comment_string2 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa

"""This is a really really really long triple quote string and it should not be touched."""

triple_quote_string = """This is a really really really long triple quote string assignment and it should not be touched."""

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception."

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception, which uses dynamic string {}.".format("formatting")

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception, which uses dynamic string %s." % "formatting"

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception, which uses dynamic %s %s." % ("string", "formatting")

some_function_call("With a reallly generic name and with a really really long string that is, at some point down the line, " + added + " to a variable and then added to another string.")

some_function_call("With a reallly generic name and with a really really long string that is, at some point down the line, " + added + " to a variable and then added to another string. But then what happens when the final string is also supppppperrrrr long?! Well then that second (realllllllly long) string should be split too.", "and a second argument", and_a_third)

return "A really really really really really really really really really really really really really long {} {}".format("return", "value")

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma which should NOT be there.",
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma which should NOT be there.", # comment after comma
)

func_with_bad_comma(
    (
        "This is a really long string argument to a function that has a trailing comma"
        " which should NOT be there."
    ),
)

func_with_bad_comma(
    (
        "This is a really long string argument to a function that has a trailing comma"
        " which should NOT be there."
    ), # comment after comma
)

func_with_bad_parens_that_wont_fit_in_one_line(
    ("short string that should have parens stripped"),
    x,
    y,
    z
)

func_with_bad_parens_that_wont_fit_in_one_line(
    x,
    y,
    ("short string that should have parens stripped"),
    z
)

func_with_bad_parens(
    ("short string that should have parens stripped"),
    x,
    y,
    z,
)

func_with_bad_parens(
    x,
    y,
    ("short string that should have parens stripped"),
    z,
)

annotated_variable: Final = "This is a large " + STRING + " that has been " + CONCATENATED + "using the '+' operator."
annotated_variable: Final = "This is a large string that has a type annotation attached to it. A type annotation should NOT stop a long string from being wrapped."
annotated_variable: Literal["fakse_literal"] = "This is a large string that has a type annotation attached to it. A type annotation should NOT stop a long string from being wrapped."

backslashes = "This is a really long string with \"embedded\" double quotes and 'single' quotes that also handles checking for an even number of backslashes \\"
backslashes = "This is a really long string with \"embedded\" double quotes and 'single' quotes that also handles checking for an even number of backslashes \\\\"
backslashes = "This is a really 'long' string with \"embedded double quotes\" and 'single' quotes that also handles checking for an odd number of backslashes \\\", like this...\\\\\\"

short_string = (
    "Hi"
    " there."
)

func_call(
    short_string=(
        "Hi"
        " there."
    )
)

raw_strings = r"Don't" " get" r" merged" " unless they are all raw."

def foo():
    yield "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."

x = f"This is a {{really}} long string that needs to be split without a doubt (i.e. most definitely). In short, this {string} that can't possibly be {{expected}} to fit all together on one line. In {fact} it may even take up three or more lines... like four or five... but probably just four."

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # type: ignore
    " of it."
)

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # noqa
    " of it."
)

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # pylint: disable=some-pylint-check
    " of it."
)

string_with_nameescape = (
    "........................................................................ \N{LAO KO LA}"
)

string_with_nameescape = (
    "........................................................................... \N{LAO KO LA}"
)

string_with_nameescape = (
    "............................................................................ \N{LAO KO LA}"
)

string_with_nameescape_and_escaped_backslash = (
    "...................................................................... \\\N{LAO KO LA}"
)

string_with_nameescape_and_escaped_backslash = (
    "......................................................................... \\\N{LAO KO LA}"
)

string_with_nameescape_and_escaped_backslash = (
    ".......................................................................... \\\N{LAO KO LA}"
)

string_with_escaped_nameescape = (
    "........................................................................ \\N{LAO KO LA}"
)

string_with_escaped_nameescape = (
    "........................................................................... \\N{LAO KO LA}"
)

msg = lambda x: f"this is a very very very long lambda value {x} that doesn't fit on a single line"

dict_with_lambda_values = {
    "join": lambda j: (
        f"{j.__class__.__name__}({some_function_call(j.left)}, "
        f"{some_function_call(j.right)})"
    ),
}

# Complex string concatenations with a method call in the middle.
code = (
    ("    return [\n")
    + (
        ", \n".join(
            "        (%r, self.%s, visitor.%s)"
            % (attrname, attrname, visit_name)
            for attrname, visit_name in names
        )
    )
    + ("\n    ]\n")
)


# Test case of an outer string' parens enclose an inner string's parens.
call(body=("%s %s" % ((",".join(items)), suffix)))


# output


x = (
    "This is a really long string that can't possibly be expected to fit all together"
    " on one line. In fact it may even take up three or more lines... like four or"
    " five... but probably just three."
)

x += (
    "This is a really long string that can't possibly be expected to fit all together"
    " on one line. In fact it may even take up three or more lines... like four or"
    " five... but probably just three."
)

y = "Short string"

print(
    "This is a really long string inside of a print statement with extra arguments"
    " attached at the end of it.",
    x,
    y,
    z,
)

print(
    "This is a really long string inside of a print statement with no extra arguments"
    " attached at the end of it."
)

D1 = {
    "The First": (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. Also it is inside a dictionary, so formatting is more"
        " difficult."
    ),
    "The Second": (
        "This is another really really (not really) long string that also can't be"
        " expected to fit on one line and is, like the other string, inside a"
        " dictionary."
    ),
}

D2 = {
    1.0: (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. Also it is inside a dictionary, so formatting is more"
        " difficult."
    ),
    2.0: (
        "This is another really really (not really) long string that also can't be"
        " expected to fit on one line and is, like the other string, inside a"
        " dictionary."
    ),
}

D3 = {
    x: (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. Also it is inside a dictionary, so formatting is more"
        " difficult."
    ),
    y: (
        "This is another really really (not really) long string that also can't be"
        " expected to fit on one line and is, like the other string, inside a"
        " dictionary."
    ),
}

D4 = {
    "A long and ridiculous {}".format(string_key): (
        "This is a really really really long string that has to go i,side of a"
        " dictionary. It is soooo bad."
    ),
    some_func("calling", "some", "stuff"): (
        "This is a really really really long string that has to go inside of a"
        " dictionary. It is {soooo} bad (#{x}).".format(sooo="soooo", x=2)
    ),
    "A %s %s"
    % ("formatted", "string"): (
        "This is a really really really long string that has to go inside of a"
        " dictionary. It is %s bad (#%d)." % ("soooo", 2)
    ),
}

D5 = {  # Test for https://github.com/psf/black/issues/3261
    "This is a really long string that can't be expected to fit in one line and is used as a nested dict's key": {
        "inner": "value"
    },
}

D6 = {  # Test for https://github.com/psf/black/issues/3261
    "This is a really long string that can't be expected to fit in one line and is used as a dict's key": [
        "value1",
        "value2",
    ],
}

L1 = [
    "The is a short string",
    (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. Also it is inside a list literal, so it's expected to"
        " be wrapped in parens when splitting to avoid implicit str concatenation."
    ),
    short_call("arg", {"key": "value"}),
    (
        "This is another really really (not really) long string that also can't be"
        " expected to fit on one line and is, like the other string, inside a list"
        " literal."
    ),
    "parens should be stripped for short string in list",
]

L2 = [
    "This is a really long string that can't be expected to fit in one line and is the"
    " only child of a list literal."
]

S1 = {
    "The is a short string",
    (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. Also it is inside a set literal, so it's expected to be"
        " wrapped in parens when splitting to avoid implicit str concatenation."
    ),
    short_call("arg", {"key": "value"}),
    (
        "This is another really really (not really) long string that also can't be"
        " expected to fit on one line and is, like the other string, inside a set"
        " literal."
    ),
    "parens should be stripped for short string in set",
}

S2 = {
    "This is a really long string that can't be expected to fit in one line and is the"
    " only child of a set literal."
}

T1 = (
    "The is a short string",
    (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. Also it is inside a tuple literal, so it's expected to"
        " be wrapped in parens when splitting to avoid implicit str concatenation."
    ),
    short_call("arg", {"key": "value"}),
    (
        "This is another really really (not really) long string that also can't be"
        " expected to fit on one line and is, like the other string, inside a tuple"
        " literal."
    ),
    "parens should be stripped for short string in list",
)

T2 = (
    (
        "This is a really long string that can't be expected to fit in one line and is"
        " the only child of a tuple literal."
    ),
)

func_with_keywords(
    my_arg,
    my_kwarg=(
        "Long keyword strings also need to be wrapped, but they will probably need to"
        " be handled a little bit differently."
    ),
)

bad_split1 = (
    "But what should happen when code has already been formatted but in the wrong way?"
    " Like with a space at the end instead of the beginning. Or what about when it is"
    " split too soon?"
)

bad_split2 = (
    "But what should happen when code has already "
    "been formatted but in the wrong way? Like "
    "with a space at the end instead of the "
    "beginning. Or what about when it is split too "
    "soon? In the case of a split that is too "
    "short, black will try to honer the custom "
    "split."
)

bad_split3 = (
    "What if we have inline comments on "  # First Comment
    "each line of a bad split? In that "  # Second Comment
    "case, we should just leave it alone."  # Third Comment
)

bad_split_func1(
    "But what should happen when code has already "
    "been formatted but in the wrong way? Like "
    "with a space at the end instead of the "
    "beginning. Or what about when it is split too "
    "soon? In the case of a split that is too "
    "short, black will try to honer the custom "
    "split.",
    xxx,
    yyy,
    zzz,
)

bad_split_func2(
    xxx,
    yyy,
    zzz,
    long_string_kwarg=(
        "But what should happen when code has already been formatted but in the wrong"
        " way? Like with a space at the end instead of the beginning. Or what about"
        " when it is split too soon?"
    ),
)

bad_split_func3(
    (
        "But what should happen when code has already "
        r"been formatted but in the wrong way? Like "
        "with a space at the end instead of the "
        r"beginning. Or what about when it is split too "
        r"soon? In the case of a split that is too "
        "short, black will try to honer the custom "
        "split."
    ),
    xxx,
    yyy,
    zzz,
)

inline_comments_func1(
    "if there are inline comments in the middle "
    # Here is the standard alone comment.
    "of the implicitly concatenated string, we should handle them correctly",
    xxx,
)

inline_comments_func2(
    "what if the string is very very very very very very very very very very long and"
    " this part does not fit into a single line? "
    # Here is the standard alone comment.
    "then the string should still be properly handled by merging and splitting "
    "it into parts that fit in line length.",
    xxx,
)

raw_string = (
    r"This is a long raw string. When re-formatting this string, black needs to make"
    r" sure it prepends the 'r' onto the new string."
)

fmt_string1 = (
    "We also need to be sure to preserve any and all {} which may or may not be"
    " attached to the string in question.".format("method calls")
)

fmt_string2 = "But what about when the string is {} but {}".format(
    "short",
    "the method call is really really really really really really really really long?",
)

old_fmt_string1 = (
    "While we are on the topic of %s, we should also note that old-style formatting"
    " must also be preserved, since some %s still uses it." % ("formatting", "code")
)

old_fmt_string2 = "This is a %s %s %s %s" % (
    "really really really really really",
    "old",
    "way to format strings!",
    "Use f-strings instead!",
)

old_fmt_string3 = (
    "Whereas only the strings after the percent sign were long in the last example,"
    " this example uses a long initial string as well. This is another %s %s %s %s"
    % (
        "really really really really really",
        "old",
        "way to format strings!",
        "Use f-strings instead!",
    )
)

fstring = (
    f"f-strings definitely make things more {difficult} than they need to be for"
    " {black}. But boy they sure are handy. The problem is that some lines will need"
    f" to have the 'f' whereas others do not. This {line}, for example, needs one."
)

fstring_with_no_fexprs = (
    f"Some regular string that needs to get split certainly but is NOT an fstring by"
    f" any means whatsoever."
)

comment_string = (  # This comment gets thrown to the top.
    "Long lines with inline comments should have their comments appended to the"
    " reformatted string's enclosing right parentheses."
)

arg_comment_string = print(
    "Long lines with inline comments which are apart of (and not the only member of) an"
    " argument list should have their comments appended to the reformatted string's"
    " enclosing left parentheses.",  # This comment gets thrown to the top.
    "Arg #2",
    "Arg #3",
    "Arg #4",
    "Arg #5",
)

pragma_comment_string1 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa: E501

pragma_comment_string2 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa

"""This is a really really really long triple quote string and it should not be touched."""

triple_quote_string = """This is a really really really long triple quote string assignment and it should not be touched."""

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception."
)

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception, which uses dynamic string {}.".format("formatting")
)

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception, which uses dynamic string %s." % "formatting"
)

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception, which uses dynamic %s %s."
    % ("string", "formatting")
)

some_function_call(
    "With a reallly generic name and with a really really long string that is, at some"
    " point down the line, "
    + added
    + " to a variable and then added to another string."
)

some_function_call(
    "With a reallly generic name and with a really really long string that is, at some"
    " point down the line, "
    + added
    + " to a variable and then added to another string. But then what happens when the"
    " final string is also supppppperrrrr long?! Well then that second (realllllllly"
    " long) string should be split too.",
    "and a second argument",
    and_a_third,
)

return (
    "A really really really really really really really really really really really"
    " really really long {} {}".format("return", "value")
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",  # comment after comma
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",  # comment after comma
)

func_with_bad_parens_that_wont_fit_in_one_line(
    "short string that should have parens stripped", x, y, z
)

func_with_bad_parens_that_wont_fit_in_one_line(
    x, y, "short string that should have parens stripped", z
)

func_with_bad_parens(
    "short string that should have parens stripped",
    x,
    y,
    z,
)

func_with_bad_parens(
    x,
    y,
    "short string that should have parens stripped",
    z,
)

annotated_variable: Final = (
    "This is a large "
    + STRING
    + " that has been "
    + CONCATENATED
    + "using the '+' operator."
)
annotated_variable: Final = (
    "This is a large string that has a type annotation attached to it. A type"
    " annotation should NOT stop a long string from being wrapped."
)
annotated_variable: Literal["fakse_literal"] = (
    "This is a large string that has a type annotation attached to it. A type"
    " annotation should NOT stop a long string from being wrapped."
)

backslashes = (
    "This is a really long string with \"embedded\" double quotes and 'single' quotes"
    " that also handles checking for an even number of backslashes \\"
)
backslashes = (
    "This is a really long string with \"embedded\" double quotes and 'single' quotes"
    " that also handles checking for an even number of backslashes \\\\"
)
backslashes = (
    "This is a really 'long' string with \"embedded double quotes\" and 'single' quotes"
    ' that also handles checking for an odd number of backslashes \\", like'
    " this...\\\\\\"
)

short_string = "Hi there."

func_call(short_string="Hi there.")

raw_strings = r"Don't" " get" r" merged" " unless they are all raw."


def foo():
    yield (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. In fact it may even take up three or more lines... like"
        " four or five... but probably just three."
    )


x = (
    "This is a {really} long string that needs to be split without a doubt (i.e."
    f" most definitely). In short, this {string} that can't possibly be {{expected}} to"
    f" fit all together on one line. In {fact} it may even take up three or more"
    " lines... like four or five... but probably just four."
)

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # type: ignore
    " of it."
)

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # noqa
    " of it."
)

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # pylint: disable=some-pylint-check
    " of it."
)

string_with_nameescape = (
    "........................................................................"
    " \N{LAO KO LA}"
)

string_with_nameescape = (
    "..........................................................................."
    " \N{LAO KO LA}"
)

string_with_nameescape = (
    "............................................................................"
    " \N{LAO KO LA}"
)

string_with_nameescape_and_escaped_backslash = (
    "......................................................................"
    " \\\N{LAO KO LA}"
)

string_with_nameescape_and_escaped_backslash = (
    "........................................................................."
    " \\\N{LAO KO LA}"
)

string_with_nameescape_and_escaped_backslash = (
    ".........................................................................."
    " \\\N{LAO KO LA}"
)

string_with_escaped_nameescape = (
    "........................................................................ \\N{LAO"
    " KO LA}"
)

string_with_escaped_nameescape = (
    "..........................................................................."
    " \\N{LAO KO LA}"
)

msg = (
    lambda x: (
        f"this is a very very very long lambda value {x} that doesn't fit on a single"
        " line"
    )
)

dict_with_lambda_values = {
    "join": lambda j: (
        f"{j.__class__.__name__}({some_function_call(j.left)}, "
        f"{some_function_call(j.right)})"
    ),
}

# Complex string concatenations with a method call in the middle.
code = (
    "    return [\n"
    + ", \n".join(
        "        (%r, self.%s, visitor.%s)" % (attrname, attrname, visit_name)
        for attrname, visit_name in names
    )
    + "\n    ]\n"
)


# Test case of an outer string' parens enclose an inner string's parens.
call(body="%s %s" % (",".join(items), suffix))
