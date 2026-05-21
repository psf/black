# flags: --unstable

[case assign_x_1]
x = "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."
# output


x = (
    "This is a really long string that can't possibly be expected to fit all together"
    " on one line. In fact it may even take up three or more lines... like four or"
    " five... but probably just three."
)

[case assign_x_2]

x += "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."
# output

x += (
    "This is a really long string that can't possibly be expected to fit all together"
    " on one line. In fact it may even take up three or more lines... like four or"
    " five... but probably just three."
)

[case assign_y]

y = (
    'Short string'
)
# output

y = "Short string"

[case print]

print('This is a really long string inside of a print statement with extra arguments attached at the end of it.', x, y, z)
# output

print(
    "This is a really long string inside of a print statement with extra arguments"
    " attached at the end of it.",
    x,
    y,
    z,
)

[case print_2]

print("This is a really long string inside of a print statement with no extra arguments attached at the end of it.")
# output

print(
    "This is a really long string inside of a print statement with no extra arguments"
    " attached at the end of it."
)

[case d1]

D1 = {"The First": "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", "The Second": "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}
# output

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

[case d2]

D2 = {1.0: "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", 2.0: "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}
# output

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

[case d3]

D3 = {x: "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", y: "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}
# output

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

[case d4]

D4 = {"A long and ridiculous {}".format(string_key): "This is a really really really long string that has to go i,side of a dictionary. It is soooo bad.", some_func("calling", "some", "stuff"): "This is a really really really long string that has to go inside of a dictionary. It is {soooo} bad (#{x}).".format(sooo="soooo", x=2), "A %s %s" % ("formatted", "string"): "This is a really really really long string that has to go inside of a dictionary. It is %s bad (#%d)." % ("soooo", 2)}
# output

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

[case d5]

D5 = {  # Test for https://github.com/psf/black/issues/3261
    ("This is a really long string that can't be expected to fit in one line and is used as a nested dict's key"): {"inner": "value"},
}
# output

D5 = {  # Test for https://github.com/psf/black/issues/3261
    "This is a really long string that can't be expected to fit in one line and is used as a nested dict's key": {
        "inner": "value"
    },
}

[case d6]

D6 = {  # Test for https://github.com/psf/black/issues/3261
    ("This is a really long string that can't be expected to fit in one line and is used as a dict's key"): ["value1", "value2"],
}
# output

D6 = {  # Test for https://github.com/psf/black/issues/3261
    "This is a really long string that can't be expected to fit in one line and is used as a dict's key": [
        "value1",
        "value2",
    ],
}

[case l1]

L1 = ["The is a short string", "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a list literal, so it's expected to be wrapped in parens when splitting to avoid implicit str concatenation.", short_call("arg", {"key": "value"}), "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a list literal.", ("parens should be stripped for short string in list")]
# output

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

[case l2]

L2 = ["This is a really long string that can't be expected to fit in one line and is the only child of a list literal."]
# output

L2 = [
    "This is a really long string that can't be expected to fit in one line and is the"
    " only child of a list literal."
]

[case s1]

S1 = {"The is a short string", "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a set literal, so it's expected to be wrapped in parens when splitting to avoid implicit str concatenation.", short_call("arg", {"key": "value"}), "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a set literal.", ("parens should be stripped for short string in set")}
# output

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

[case s2]

S2 = {"This is a really long string that can't be expected to fit in one line and is the only child of a set literal."}
# output

S2 = {
    "This is a really long string that can't be expected to fit in one line and is the"
    " only child of a set literal."
}

[case t1]

T1 = ("The is a short string", "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a tuple literal, so it's expected to be wrapped in parens when splitting to avoid implicit str concatenation.", short_call("arg", {"key": "value"}), "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a tuple literal.", ("parens should be stripped for short string in list"))
# output

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

[case t2]

T2 = ("This is a really long string that can't be expected to fit in one line and is the only child of a tuple literal.",)
# output

T2 = (
    (
        "This is a really long string that can't be expected to fit in one line and is"
        " the only child of a tuple literal."
    ),
)

[case test_case_for_https_github_com_psf_black_issues_4912_unassig]

# Test case for https://github.com/psf/black/issues/4912 - unassigned long string with trailing comma
"A long string literal that is not assigned to a variable, exceeds line length when string-processing is enabled, and has a trailing comma (to make it a one-item tuple)",
# output

# Test case for https://github.com/psf/black/issues/4912 - unassigned long string with trailing comma
(
    "A long string literal that is not assigned to a variable, exceeds line length when"
    " string-processing is enabled, and has a trailing comma (to make it a one-item"
    " tuple)"
),

[case func_with_keywords]

func_with_keywords(my_arg, my_kwarg="Long keyword strings also need to be wrapped, but they will probably need to be handled a little bit differently.")
# output

func_with_keywords(
    my_arg,
    my_kwarg=(
        "Long keyword strings also need to be wrapped, but they will probably need to"
        " be handled a little bit differently."
    ),
)

[case bad_split1]

bad_split1 = (
    'But what should happen when code has already been formatted but in the wrong way? Like'
    " with a space at the end instead of the beginning. Or what about when it is split too soon?"
)
# output

bad_split1 = (
    "But what should happen when code has already been formatted but in the wrong way?"
    " Like with a space at the end instead of the beginning. Or what about when it is"
    " split too soon?"
)

[case bad_split2]

bad_split2 = "But what should happen when code has already " \
             "been formatted but in the wrong way? Like " \
             "with a space at the end instead of the " \
             "beginning. Or what about when it is split too " \
             "soon? In the case of a split that is too " \
             "short, black will try to honer the custom " \
             "split."
# output

bad_split2 = (
    "But what should happen when code has already "
    "been formatted but in the wrong way? Like "
    "with a space at the end instead of the "
    "beginning. Or what about when it is split too "
    "soon? In the case of a split that is too "
    "short, black will try to honer the custom "
    "split."
)

[case bad_split3]

bad_split3 = (
    "What if we have inline comments on "  # First Comment
    "each line of a bad split? In that "  # Second Comment
    "case, we should just leave it alone."  # Third Comment
)
# output

bad_split3 = (
    "What if we have inline comments on "  # First Comment
    "each line of a bad split? In that "  # Second Comment
    "case, we should just leave it alone."  # Third Comment
)

[case bad_split_func1]

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
# output

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

[case bad_split_func2]

bad_split_func2(
    xxx, yyy, zzz,
    long_string_kwarg="But what should happen when code has already been formatted but in the wrong way? Like "
                      "with a space at the end instead of the beginning. Or what about when it is split too "
                      "soon?",
)
# output

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

[case bad_split_func3]

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
# output

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

[case inline_comments_func1]

inline_comments_func1(
    "if there are inline "
    "comments in the middle "
    # Here is the standard alone comment.
    "of the implicitly concatenated "
    "string, we should handle "
    "them correctly",
    xxx,
)
# output

inline_comments_func1(
    "if there are inline comments in the middle "
    # Here is the standard alone comment.
    "of the implicitly concatenated string, we should handle them correctly",
    xxx,
)

[case inline_comments_func2]

inline_comments_func2(
    "what if the string is very very very very very very very very very very long and this part does "
    "not fit into a single line? "
    # Here is the standard alone comment.
    "then the string should still be properly handled by merging and splitting "
    "it into parts that fit in line length.",
    xxx,
)
# output

inline_comments_func2(
    "what if the string is very very very very very very very very very very long and"
    " this part does not fit into a single line? "
    # Here is the standard alone comment.
    "then the string should still be properly handled by merging and splitting "
    "it into parts that fit in line length.",
    xxx,
)

[case raw_string]

raw_string = r"This is a long raw string. When re-formatting this string, black needs to make sure it prepends the 'r' onto the new string."
# output

raw_string = (
    r"This is a long raw string. When re-formatting this string, black needs to make"
    r" sure it prepends the 'r' onto the new string."
)

[case fmt_string1]

fmt_string1 = "We also need to be sure to preserve any and all {} which may or may not be attached to the string in question.".format("method calls")
# output

fmt_string1 = (
    "We also need to be sure to preserve any and all {} which may or may not be"
    " attached to the string in question.".format("method calls")
)

[case fmt_string2]

fmt_string2 = "But what about when the string is {} but {}".format("short", "the method call is really really really really really really really really long?")
# output

fmt_string2 = "But what about when the string is {} but {}".format(
    "short",
    "the method call is really really really really really really really really long?",
)

[case old_fmt_string1]

old_fmt_string1 = "While we are on the topic of %s, we should also note that old-style formatting must also be preserved, since some %s still uses it." % ("formatting", "code")
# output

old_fmt_string1 = (
    "While we are on the topic of %s, we should also note that old-style formatting"
    " must also be preserved, since some %s still uses it." % ("formatting", "code")
)

[case old_fmt_string2]

old_fmt_string2 = "This is a %s %s %s %s" % ("really really really really really", "old", "way to format strings!", "Use f-strings instead!")
# output

old_fmt_string2 = "This is a %s %s %s %s" % (
    "really really really really really",
    "old",
    "way to format strings!",
    "Use f-strings instead!",
)

[case old_fmt_string3]

old_fmt_string3 = "Whereas only the strings after the percent sign were long in the last example, this example uses a long initial string as well. This is another %s %s %s %s" % ("really really really really really", "old", "way to format strings!", "Use f-strings instead!")
# output

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

[case fstring]

fstring = f"f-strings definitely make things more {difficult} than they need to be for {{black}}. But boy they sure are handy. The problem is that some lines will need to have the 'f' whereas others do not. This {line}, for example, needs one."
# output

fstring = (
    f"f-strings definitely make things more {difficult} than they need to be for"
    " {black}. But boy they sure are handy. The problem is that some lines will need"
    f" to have the 'f' whereas others do not. This {line}, for example, needs one."
)

[case fstring_with_no_fexprs]

fstring_with_no_fexprs = f"Some regular string that needs to get split certainly but is NOT an fstring by any means whatsoever."
# output

fstring_with_no_fexprs = (
    f"Some regular string that needs to get split certainly but is NOT an fstring by"
    f" any means whatsoever."
)

[case comment_string]

comment_string = "Long lines with inline comments should have their comments appended to the reformatted string's enclosing right parentheses."  # This comment gets thrown to the top.
# output

comment_string = (  # This comment gets thrown to the top.
    "Long lines with inline comments should have their comments appended to the"
    " reformatted string's enclosing right parentheses."
)

[case arg_comment_string]

arg_comment_string = print("Long lines with inline comments which are apart of (and not the only member of) an argument list should have their comments appended to the reformatted string's enclosing left parentheses.",  # This comment gets thrown to the top.
    "Arg #2", "Arg #3", "Arg #4", "Arg #5")
# output

arg_comment_string = print(
    "Long lines with inline comments which are apart of (and not the only member of) an"
    " argument list should have their comments appended to the reformatted string's"
    " enclosing left parentheses.",  # This comment gets thrown to the top.
    "Arg #2",
    "Arg #3",
    "Arg #4",
    "Arg #5",
)

[case pragma_comment_string1]

pragma_comment_string1 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa: E501
# output

pragma_comment_string1 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa: E501

[case pragma_comment_string2]

pragma_comment_string2 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa
# output

pragma_comment_string2 = "Lines which end with an inline pragma comment of the form `# <pragma>: <...>` should be left alone."  # noqa

[case this]

"""This is a really really really long triple quote string and it should not be touched."""
# output

"""This is a really really really long triple quote string and it should not be touched."""

[case triple_quote_string]

triple_quote_string = """This is a really really really long triple quote string assignment and it should not be touched."""
# output

triple_quote_string = """This is a really really really long triple quote string assignment and it should not be touched."""

[case assert]

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception."
# output

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception."
)

[case assert_2]

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception, which uses dynamic string {}.".format("formatting")
# output

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception, which uses dynamic string {}.".format("formatting")
)

[case assert_3]

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception, which uses dynamic string %s." % "formatting"
# output

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception, which uses dynamic string %s." % "formatting"
)

[case assert_4]

assert some_type_of_boolean_expression, "Followed by a really really really long string that is used to provide context to the AssertionError exception, which uses dynamic %s %s." % ("string", "formatting")
# output

assert some_type_of_boolean_expression, (
    "Followed by a really really really long string that is used to provide context to"
    " the AssertionError exception, which uses dynamic %s %s."
    % ("string", "formatting")
)

[case some_function_call]

some_function_call("With a reallly generic name and with a really really long string that is, at some point down the line, " + added + " to a variable and then added to another string.")
# output

some_function_call(
    "With a reallly generic name and with a really really long string that is, at some"
    " point down the line, "
    + added
    + " to a variable and then added to another string."
)

[case some_function_call_2]

some_function_call("With a reallly generic name and with a really really long string that is, at some point down the line, " + added + " to a variable and then added to another string. But then what happens when the final string is also supppppperrrrr long?! Well then that second (realllllllly long) string should be split too.", "and a second argument", and_a_third)
# output

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

[case return]

return "A really really really really really really really really really really really really really long {} {}".format("return", "value")
# output

return (
    "A really really really really really really really really really really really"
    " really really long {} {}".format("return", "value")
)

[case func_with_bad_comma]

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma which should NOT be there.",
)
# output

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",
)

[case func_with_bad_comma_2]

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma which should NOT be there.", # comment after comma
)
# output

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",  # comment after comma
)

[case func_with_bad_comma_3]

func_with_bad_comma(
    (
        "This is a really long string argument to a function that has a trailing comma"
        " which should NOT be there."
    ),
)
# output

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",
)

[case func_with_bad_comma_4]

func_with_bad_comma(
    (
        "This is a really long string argument to a function that has a trailing comma"
        " which should NOT be there."
    ), # comment after comma
)
# output

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there.",  # comment after comma
)

[case func_with_bad_parens_that_wont_fit_in_one_line]

func_with_bad_parens_that_wont_fit_in_one_line(
    ("short string that should have parens stripped"),
    x,
    y,
    z
)
# output

func_with_bad_parens_that_wont_fit_in_one_line(
    "short string that should have parens stripped", x, y, z
)

[case func_with_bad_parens_that_wont_fit_in_one_line_2]

func_with_bad_parens_that_wont_fit_in_one_line(
    x,
    y,
    ("short string that should have parens stripped"),
    z
)
# output

func_with_bad_parens_that_wont_fit_in_one_line(
    x, y, "short string that should have parens stripped", z
)

[case func_with_bad_parens]

func_with_bad_parens(
    ("short string that should have parens stripped"),
    x,
    y,
    z,
)
# output

func_with_bad_parens(
    "short string that should have parens stripped",
    x,
    y,
    z,
)

[case func_with_bad_parens_2]

func_with_bad_parens(
    x,
    y,
    ("short string that should have parens stripped"),
    z,
)
# output

func_with_bad_parens(
    x,
    y,
    "short string that should have parens stripped",
    z,
)

[case annotated_variable]

annotated_variable: Final = "This is a large " + STRING + " that has been " + CONCATENATED + "using the '+' operator."
# output

annotated_variable: Final = (
    "This is a large "
    + STRING
    + " that has been "
    + CONCATENATED
    + "using the '+' operator."
)

[case annotated_variable_2]
annotated_variable: Final = "This is a large string that has a type annotation attached to it. A type annotation should NOT stop a long string from being wrapped."
# output
annotated_variable: Final = (
    "This is a large string that has a type annotation attached to it. A type"
    " annotation should NOT stop a long string from being wrapped."
)

[case annotated_variable_3]
annotated_variable: Literal["fakse_literal"] = "This is a large string that has a type annotation attached to it. A type annotation should NOT stop a long string from being wrapped."
# output
annotated_variable: Literal["fakse_literal"] = (
    "This is a large string that has a type annotation attached to it. A type"
    " annotation should NOT stop a long string from being wrapped."
)

[case backslashes]

backslashes = "This is a really long string with \"embedded\" double quotes and 'single' quotes that also handles checking for an even number of backslashes \\"
# output

backslashes = (
    "This is a really long string with \"embedded\" double quotes and 'single' quotes"
    " that also handles checking for an even number of backslashes \\"
)

[case backslashes_2]
backslashes = "This is a really long string with \"embedded\" double quotes and 'single' quotes that also handles checking for an even number of backslashes \\\\"
# output
backslashes = (
    "This is a really long string with \"embedded\" double quotes and 'single' quotes"
    " that also handles checking for an even number of backslashes \\\\"
)

[case backslashes_3]
backslashes = "This is a really 'long' string with \"embedded double quotes\" and 'single' quotes that also handles checking for an odd number of backslashes \\\", like this...\\\\\\"
# output
backslashes = (
    "This is a really 'long' string with \"embedded double quotes\" and 'single' quotes"
    ' that also handles checking for an odd number of backslashes \\", like'
    " this...\\\\\\"
)

[case short_string]

short_string = (
    "Hi"
    " there."
)
# output

short_string = "Hi there."

[case func_call]

func_call(
    short_string=(
        "Hi"
        " there."
    )
)
# output

func_call(short_string="Hi there.")

[case raw_strings]

raw_strings = r"Don't" " get" r" merged" " unless they are all raw."
# output

raw_strings = r"Don't" " get" r" merged" " unless they are all raw."

[case fn_foo]

def foo():
    yield "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."
# output


def foo():
    yield (
        "This is a really long string that can't possibly be expected to fit all"
        " together on one line. In fact it may even take up three or more lines... like"
        " four or five... but probably just three."
    )

[case assign_x_3]

x = f"This is a {{really}} long string that needs to be split without a doubt (i.e. most definitely). In short, this {string} that can't possibly be {{expected}} to fit all together on one line. In {fact} it may even take up three or more lines... like four or five... but probably just four."
# output


x = (
    "This is a {really} long string that needs to be split without a doubt (i.e."
    f" most definitely). In short, this {string} that can't possibly be {{expected}} to"
    f" fit all together on one line. In {fact} it may even take up three or more"
    " lines... like four or five... but probably just four."
)

[case long_unmergable_string_with_pragma]

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # type: ignore
    " of it."
)
# output

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # type: ignore
    " of it."
)

[case long_unmergable_string_with_pragma_2]

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # noqa
    " of it."
)
# output

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # noqa
    " of it."
)

[case long_unmergable_string_with_pragma_3]

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # pylint: disable=some-pylint-check
    " of it."
)
# output

long_unmergable_string_with_pragma = (
    "This is a really long string that can't be merged because it has a likely pragma at the end"  # pylint: disable=some-pylint-check
    " of it."
)

[case string_with_nameescape]

string_with_nameescape = (
    "........................................................................ \N{LAO KO LA}"
)
# output

string_with_nameescape = (
    "........................................................................"
    " \N{LAO KO LA}"
)

[case string_with_nameescape_2]

string_with_nameescape = (
    "........................................................................... \N{LAO KO LA}"
)
# output

string_with_nameescape = (
    "..........................................................................."
    " \N{LAO KO LA}"
)

[case string_with_nameescape_3]

string_with_nameescape = (
    "............................................................................ \N{LAO KO LA}"
)
# output

string_with_nameescape = (
    "............................................................................"
    " \N{LAO KO LA}"
)

[case string_with_nameescape_and_escaped_backslash]

string_with_nameescape_and_escaped_backslash = (
    "...................................................................... \\\N{LAO KO LA}"
)
# output

string_with_nameescape_and_escaped_backslash = (
    "......................................................................"
    " \\\N{LAO KO LA}"
)

[case string_with_nameescape_and_escaped_backslash_2]

string_with_nameescape_and_escaped_backslash = (
    "......................................................................... \\\N{LAO KO LA}"
)
# output

string_with_nameescape_and_escaped_backslash = (
    "........................................................................."
    " \\\N{LAO KO LA}"
)

[case string_with_nameescape_and_escaped_backslash_3]

string_with_nameescape_and_escaped_backslash = (
    ".......................................................................... \\\N{LAO KO LA}"
)
# output

string_with_nameescape_and_escaped_backslash = (
    ".........................................................................."
    " \\\N{LAO KO LA}"
)

[case string_with_escaped_nameescape]

string_with_escaped_nameescape = (
    "........................................................................ \\N{LAO KO LA}"
)
# output

string_with_escaped_nameescape = (
    "........................................................................ \\N{LAO"
    " KO LA}"
)

[case string_with_escaped_nameescape_2]

string_with_escaped_nameescape = (
    "........................................................................... \\N{LAO KO LA}"
)
# output

string_with_escaped_nameescape = (
    "..........................................................................."
    " \\N{LAO KO LA}"
)

[case msg]

msg = lambda x: f"this is a very very very very long lambda value {x} that doesn't fit on a single line"
# output

msg = lambda x: (
    f"this is a very very very very long lambda value {x} that doesn't fit on a"
    " single line"
)

[case dict_with_lambda_values]

dict_with_lambda_values = {
    "join": lambda j: (
        f"{j.__class__.__name__}({some_function_call(j.left)}, "
        f"{some_function_call(j.right)})"
    ),
}
# output

dict_with_lambda_values = {
    "join": lambda j: (
        f"{j.__class__.__name__}({some_function_call(j.left)}, "
        f"{some_function_call(j.right)})"
    ),
}

[case complex_string_concatenations_with_a_method_call_in_the_midd]

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
# output

# Complex string concatenations with a method call in the middle.
code = (
    "    return [\n"
    + ", \n".join(
        "        (%r, self.%s, visitor.%s)" % (attrname, attrname, visit_name)
        for attrname, visit_name in names
    )
    + "\n    ]\n"
)

[case test_case_of_an_outer_string_parens_enclose_an_inner_string]


# Test case of an outer string' parens enclose an inner string's parens.
call(body=("%s %s" % ((",".join(items)), suffix)))
# output


# Test case of an outer string' parens enclose an inner string's parens.
call(body="%s %s" % (",".join(items), suffix))

[case log]

log.info(f'Skipping: {desc["db_id"]=} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]=} {desc["exposure_max"]=}')
# output

log.info(
    f'Skipping: {desc["db_id"]=} {desc["ms_name"]} {money=} {dte=} {pos_share=}'
    f' {desc["status"]=} {desc["exposure_max"]=}'
)

[case log_2]

log.info(f"Skipping: {desc['db_id']=} {desc['ms_name']} {money=} {dte=} {pos_share=} {desc['status']=} {desc['exposure_max']=}")
# output

log.info(
    f"Skipping: {desc['db_id']=} {desc['ms_name']} {money=} {dte=} {pos_share=}"
    f" {desc['status']=} {desc['exposure_max']=}"
)

[case log_3]

log.info(f'Skipping: {desc["db_id"]} {foo("bar",x=123)} {"foo" != "bar"} {(x := "abc=")} {pos_share=} {desc["status"]} {desc["exposure_max"]}')
# output

log.info(
    f'Skipping: {desc["db_id"]} {foo("bar",x=123)} {"foo" != "bar"} {(x := "abc=")}'
    f' {pos_share=} {desc["status"]} {desc["exposure_max"]}'
)

[case log_4]

log.info(f'Skipping: {desc["db_id"]} {desc["ms_name"]} {money=} {(x := "abc=")=} {pos_share=} {desc["status"]} {desc["exposure_max"]}')
# output

log.info(
    f'Skipping: {desc["db_id"]} {desc["ms_name"]} {money=} {(x := "abc=")=}'
    f' {pos_share=} {desc["status"]} {desc["exposure_max"]}'
)

[case log_5]

log.info(f'Skipping: {desc["db_id"]} {foo("bar",x=123)=} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}')
# output

log.info(
    f'Skipping: {desc["db_id"]} {foo("bar",x=123)=} {money=} {dte=} {pos_share=}'
    f' {desc["status"]} {desc["exposure_max"]}'
)

[case log_6]

log.info(f'Skipping: {foo("asdf")=} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}')
# output

log.info(
    f'Skipping: {foo("asdf")=} {desc["ms_name"]} {money=} {dte=} {pos_share=}'
    f' {desc["status"]} {desc["exposure_max"]}'
)

[case log_7]

log.info(f'Skipping: {"a" == "b" == "c" == "d"} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}')
# output

log.info(
    f'Skipping: {"a" == "b" == "c" == "d"} {desc["ms_name"]} {money=} {dte=}'
    f' {pos_share=} {desc["status"]} {desc["exposure_max"]}'
)

[case log_8]

log.info(f'Skipping: {"a" == "b" == "c" == "d"=} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}')
# output

log.info(
    f'Skipping: {"a" == "b" == "c" == "d"=} {desc["ms_name"]} {money=} {dte=}'
    f' {pos_share=} {desc["status"]} {desc["exposure_max"]}'
)

[case log_9]

log.info(f'Skipping: {  longer_longer_longer_longer_longer_longer_name   [ "db_id" ]      [ "another_key" ]   =  :  .3f }')
# output

log.info(
    "Skipping:"
    f' {  longer_longer_longer_longer_longer_longer_name   [ "db_id" ]      [ "another_key" ]   =  :  .3f }'
)

[case log_10]

log.info(f'''Skipping: {"a" == 'b'} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}''')
# output

log.info(
    f"""Skipping: {"a" == 'b'} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}"""
)

[case log_11]

log.info(f'''Skipping: {'a' == "b"=} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}''')
# output

log.info(
    f"""Skipping: {'a' == "b"=} {desc["ms_name"]} {money=} {dte=} {pos_share=} {desc["status"]} {desc["exposure_max"]}"""
)

[case log_12]

log.info(f"""Skipping: {'a' == 'b'} {desc['ms_name']} {money=} {dte=} {pos_share=} {desc['status']} {desc['exposure_max']}""")
# output

log.info(
    f"""Skipping: {'a' == 'b'} {desc['ms_name']} {money=} {dte=} {pos_share=} {desc['status']} {desc['exposure_max']}"""
)

[case assign_x_4]

x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    )
}
# output

x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    )
}

[case assign_x_5]
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx",
}
# output
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxxx{xx}xxx_xxxxx_xxxxxxxxx_xxxxxxxxxxxx_xxxx"
    ),
}

[case assign_x_6]
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": (
        "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxx"
    )
}
# output
x = {
    "xx_xxxxx_xxxxxxxxxx_xxxxxxxxx_xx": "xx:xxxxxxxxxxxxxxxxx_xxxxx_xxxxxxx_xxxxxxxxxx"
}
