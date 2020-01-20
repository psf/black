x = "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."

x += "This is a really long string that can't possibly be expected to fit all together on one line. In fact it may even take up three or more lines... like four or five... but probably just three."

y = (
    "Short string"
)

print("This is a really long string inside of a print statement with extra arguments attached at the end of it.", x, y, z)

print("This is a really long string inside of a print statement with no extra arguments attached at the end of it.")

D1 = {"The First": "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", "The Second": "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}

D2 = {1.0: "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", 2.0: "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}

D3 = {x: "This is a really long string that can't possibly be expected to fit all together on one line. Also it is inside a dictionary, so formatting is more difficult.", y: "This is another really really (not really) long string that also can't be expected to fit on one line and is, like the other string, inside a dictionary."}

D4 = {"A long and ridiculous {}".format(string_key): "This is a really really really long string that has to go i,side of a dictionary. It is soooo bad.", some_func("calling", "some", "stuff"): "This is a really really really long string that has to go inside of a dictionary. It is {soooo} bad (#{x}).".format(sooo="soooo", x=2), "A %s %s" % ("formatted", "string"): "This is a really really really long string that has to go inside of a dictionary. It is %s bad (#%d)." % ("soooo", 2)}

func_with_keywords(my_arg, my_kwarg="Long keyword strings also need to be wrapped, but they will probably need to be handled a little bit differently.")

bad_split1 = (
    "But what should happen when code has already been formatted but in the wrong way? Like"
    " with a space at the beginning instead of the end. Or what about when it is split too soon?"
)

bad_split2 = "But what should happen when code has already " \
             "been formatted but in the wrong way? Like " \
             "with a space at the beginning instead of the " \
             "end. Or what about when it is split too " \
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
    "with a space at the beginning instead of the "
    "end. Or what about when it is split too "
    "soon? In the case of a split that is too "
    "short, black will try to honer the custom "
    "split.",
    xxx, yyy, zzz
)

bad_split_func2(
    xxx, yyy, zzz,
    long_string_kwarg="But what should happen when code has already been formatted but in the wrong way? Like "
                      "with a space at the beginning instead of the end. Or what about when it is split too "
                      "soon?",
)

bad_split_func3(
    (
        "But what should happen when code has already "
        r"been formatted but in the wrong way? Like "
        "with a space at the beginning instead of the "
        r"end. Or what about when it is split too "
        r"soon? In the case of a split that is too "
        "short, black will try to honer the custom "
        "split."
    ),
    xxx,
    yyy,
    zzz,
)

raw_string = r"This is a long raw string. When re-formatting this string, black needs to make sure it prepends the 'r' onto the new string."

fmt_string1 = "We also need to be sure to preserve any and all {} which may or may not be attached to the string in question.".format("method calls")

fmt_string2 = "But what about when the string is {} but {}".format("short", "the method call is really really really really really really really really long?")

old_fmt_string1 = "While we are on the topic of %s, we should also note that old-style formatting must also be preserved, since some %s still uses it." % ("formatting", "code")

old_fmt_string2 = "This is a %s %s %s %s" % ("really really really really really", "old", "way to format strings!", "Use f-strings instead!")

old_fmt_string3 = "Whereas only the strings after the percent sign were long in the last example, this example uses a long initial string as well. This is another %s %s %s %s" % ("really really really really really", "old", "way to format strings!", "Use f-strings instead!")

fstring = f"f-strings definitely make things more {difficult} than they need to be for black. But boy they sure are handy. The problem is that some lines will need to have the 'f' whereas others do not. This {line}, for example, needs one."

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

########## REGRESSION TESTS ##########
# There was a bug where tuples were being identified as long strings.
long_tuple = ('Apple', 'Berry', 'Cherry', 'Dill', 'Evergreen', 'Fig',
           'Grape', 'Harry', 'Iglu', 'Jaguar')

stupid_format_method_bug = "Some really long string that just so happens to be the {} {} to force the 'format' method to hang over the line length boundary. This is pretty annoying.".format("perfect", "length")

class A:
    def foo():
        os.system("This is a regression test. xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxxx.".format("xxxxxxxxxx", "xxxxxx", "xxxxxxxxxx"))


class A:
    def foo():
        XXXXXXXXXXXX.append(
            (
                "xxx_xxxxxxxxxx(xxxxx={}, xxxx={}, xxxxx, xxxx_xxxx_xxxxxxxxxx={})".format(
                    xxxxx, xxxx, xxxx_xxxx_xxxxxxxxxx
                ),
                my_var,
                my_other_var,
            )
        )

class A:
    class B:
        def foo():
            bar(
                (
                    "[{}]: xxx_xxxxxxxxxx(xxxxx={}, xxxx={}, xxxxx={}"
                    " xxxx_xxxx_xxxxxxxxxx={}, xxxx={})"
                    .format(xxxx._xxxxxxxxxxxxxx, xxxxx, xxxx, xxxx_xxxx_xxxxxxxxxx, xxxxxxx)
                ),
                varX,
                varY,
                varZ,
            )

def foo(xxxx):
    for (xxx_xxxx, _xxx_xxx, _xxx_xxxxx, xxx_xxxx) in xxxx:
        for xxx in xxx_xxxx:
            assert ("x" in xxx) or (
                xxx in xxx_xxx_xxxxx
            ), "{0} xxxxxxx xx {1}, xxx {1} xx xxx xx xxxx xx xxx xxxx: xxx xxxx {2}".format(
                xxx_xxxx, xxx, xxxxxx.xxxxxxx(xxx_xxx_xxxxx)
            )

class A:
    def disappearing_comment():
        return (
            (  # xx -x xxxxxxx xx xxx xxxxxxx.
                '{{xxx_xxxxxxxxxx_xxxxxxxx}} xxx xxxx'
                ' {} {{xxxx}} >&2'
                .format(
                    "{xxxx} {xxxxxx}"
                    if xxxxx.xx_xxxxxxxxxx
                    else ( # Disappearing Comment
                        "--xxxxxxx --xxxxxx=x --xxxxxx-xxxxx=xxxxxx"
                        " --xxxxxx-xxxx=xxxxxxxxxxx.xxx"
                    )
                )
            ),
            (x, y, z),
        )

class A:
    class B:
        def foo():
            xxxxx_xxxx(
                xx, "\t"
                "@xxxxxx '{xxxx_xxx}\t' > {xxxxxx_xxxx}.xxxxxxx;"
                "{xxxx_xxx} >> {xxxxxx_xxxx}.xxxxxxx 2>&1; xx=$$?;"
                "xxxx $$xx"
                .format(xxxx_xxx=xxxx_xxxxxxx, xxxxxx_xxxx=xxxxxxx + "/" + xxxx_xxx_xxxx, x=xxx_xxxxx_xxxxx_xxx),
                x,
                y,
                z,
            )

func_call_where_string_arg_has_method_call_and_bad_parens(
    (
        "A long string with {}. This string is so long that it is ridiculous. It can't fit on one line at alllll.".format("formatting")
    ),
)

func_call_where_string_arg_has_old_fmt_and_bad_parens(
    (
        "A long string with {}. This string is so long that it is ridiculous. It can't fit on one line at alllll." % "formatting"
    ),
)

func_call_where_string_arg_has_old_fmt_and_bad_parens(
    (
        "A long string with {}. This {} is so long that it is ridiculous. It can't fit on one line at alllll." % ("formatting", "string")
    ),
)

class A:
    def append(self):
        if True:
            xxxx.xxxxxxx.xxxxx( ('xxxxxxxxxx xxxx xx xxxxxx(%x) xx %x xxxx xx xxx %x.xx'
                                 % (len(self) + 1,
                                    xxxx.xxxxxxxxxx,
                                    xxxx.xxxxxxxxxx))
                                + (' %.3f (%s) to %.3f (%s).\n'
                                   % (xxxx.xxxxxxxxx,
                                      xxxx.xxxxxxxxxxxxxx(xxxx.xxxxxxxxx),
                                      x,
                                      xxxx.xxxxxxxxxxxxxx( xx)
                                      )))

class A:
    def foo():
        some_func_call(
            'xxxxxxxxxx',
            (
                "xx {xxxxxxxxxxx}/xxxxxxxxxxx.xxx xxxx.xxx && xxxxxx -x "
                "\"xxxx xxxxxxx xxxxxx xxxx; xxxx xxxxxx_xxxxx xxxxxx xxxx; "
                "xxxx.xxxx_xxxxxx(['xxxx.xxx'], xxxx.xxxxxxx().xxxxxxxxxx)\" "
            ),
            None,
            ('xxxxxxxxxxx',),
        ),

class A:
    def foo():
        some_func_call(
            (
                "xx {xxxxxxxxxxx}/xxxxxxxxxxx.xxx xxxx.xxx && xxxxxx -x "
                "xxxx, ('xxxxxxx xxxxxx xxxx, xxxx') xxxxxx_xxxxx xxxxxx xxxx; "
                "xxxx.xxxx_xxxxxx(['xxxx.xxx'], xxxx.xxxxxxx().xxxxxxxxxx)\" "
            ),
            None,
            ('xxxxxxxxxxx',),
        ),

xxxxxxx = { 'xx' : 'xxxx xxxxxxx xxxxxxxxx -x xxx -x /xxx/{0} -x xxx,xxx -xx {1} \
-xx {1} -xx xxx=xxx_xxxx,xxx_xx,xxx_xxx,xxx_xxxx,xxx_xx,xxx_xxx |\
 xxxxxx -x xxxxxxxx -x xxxxxxxx -x',
         'xx' : 'xxxx xxxxxxx xxxxxxxxx -x xxx -x /xxx/{0} -x xxx,xxx -xx {1} \
-xx {1} -xx xxx=xxx_xxxx_xxx_xxxx,xxx_xx_xxx_xxxx,xxx_xxxx_xxx_xxxx,\
xxx_xx_xxxx_xxxx,xxx_xxx_xxxx,xxx_xxx_xxxx xxxx=xxx | xxxxxx -x xxxxxxxx -x xxxxxxxx -x'
}

class A:
    def foo(self):
        if True:
            xxxxx_xxxxxxxxxxxx('xxx xxxxxx xxx xxxxxxxxx.xx xx xxxxxxxx.  xxx xxxxxxxxxxxxx.xx xxxxxxx '
                               + 'xx xxxxxx xxxxxx xxxxxx xx xxxxxxx xxx xxx ${0} xx x xxxxxxxx xxxxx'.xxxxxx(xxxxxx_xxxxxx_xxx))

class A:
    class B:
        def foo():
            row = {
                'xxxxxxxxxxxxxxx' : xxxxxx_xxxxx_xxxx,
                # 'xxxxxxxxxxxxxxxxxxxxxxx'
                # 'xxxxxxxxxxxxxxxxxxxxxx'
                # 'xxxxxxxxxxxxxxxxxx'
                # 'xxxxxxxxxxxxxxxxx'
                'xxxxxxxxxx' : xxxxx_xxxxx,
                }

class A:
    def xxxx_xxx_xx_xxxxxxxxxx_xxxx_xxxxxxxxx(xxxx):
        xxxxxxxx = [
            xxxxxxxxxxxxxxxx(
                'xxxx',
                xxxxxxxxxxx={
                    'xxxx' : 1.0,
                },
                xxxxxx={'xxxxxx 1' : xxxxxx(xxxx='xxxxxx 1', xxxxxx=600.0)},
                xxxxxxxx_xxxxxxx=0.0,
            ),
            xxxxxxxxxxxxxxxx(
                'xxxxxxx',
                xxxxxxxxxxx={
                    'xxxx' : 1.0,
                },
                xxxxxx={'xxxxxx 1' : xxxxxx(xxxx='xxxxxx 1', xxxxxx=200.0)},
                xxxxxxxx_xxxxxxx=0.0,
            ),
            xxxxxxxxxxxxxxxx(
                'xxxx',
            ),
        ]

some_dictionary = {
    'xxxxx006': ['xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx0xx6xxxxxxxxxx2xxxxxx9xxxxxxxxxx0xxxxx1xxx2x/xx9xx6+x+xxxxxxxxxxxxxx4xxxxxxxxxxxxxxxxxxxxx43xxx2xx2x4x++xxx6xxxxxxxxx+xxxxx/xx9x+xxxxxxxxxxxxxx8x15xxxxxxxxxxxxxxxxx82xx/xxxxxxxxxxxxxx/x5xxxxxxxxxxxxxx6xxxxxx74x4/xxx4x+xxxxxxxxx2xxxxxxxx87xxxxx4xxxxxxxx3xx0xxxxx4xxx1xx9xx5xxxxxxx/xxxxx5xx6xx4xxxx1x/x2xxxxxxxxxxxx64xxxxxxx1x0xx5xxxxxxxxxxxxxx== xxxxx000 xxxxxxxxxx\n',
                 'xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx6xxxxxxxxxxxxxx9xxxxxxxxxxxxx3xxx9xxxxxxxxxxxxxxxx0xxxxxxxxxxxxxxxxx2xxxx2xxx6xxxxx/xx54xxxxxxxxx4xxx3xxxxxx9xx3xxxxx39xxxxxxxxx5xx91xxxx7xxxxxx8xxxxxxxxxxxxxxxx9xxx93xxxxxxxxxxxxxxxxx7xxx8xx8xx4/x1xxxxx1x3xxxxxxxxxxxxx3xxxxxx9xx4xx4x7xxxxxxxxxxxxx1xxxxxxxxx7xxxxxxxxxxxxxx4xx6xxxxxxxxx9xxx7xxxx2xxxxxxxxxxxxxxxxxxxxxx8xxxxxxxxxxxxxxxxxxxx6xx== xxxxx010 xxxxxxxxxx\n'],
    'xxxxx016': ['xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx0xx6xxxxxxxxxx2xxxxxx9xxxxxxxxxx0xxxxx1xxx2x/xx9xx6+x+xxxxxxxxxxxxxx4xxxxxxxxxxxxxxxxxxxxx43xxx2xx2x4x++xxx6xxxxxxxxx+xxxxx/xx9x+xxxxxxxxxxxxxx8x15xxxxxxxxxxxxxxxxx82xx/xxxxxxxxxxxxxx/x5xxxxxxxxxxxxxx6xxxxxx74x4/xxx4x+xxxxxxxxx2xxxxxxxx87xxxxx4xxxxxxxx3xx0xxxxx4xxx1xx9xx5xxxxxxx/xxxxx5xx6xx4xxxx1x/x2xxxxxxxxxxxx64xxxxxxx1x0xx5xxxxxxxxxxxxxx== xxxxx000 xxxxxxxxxx\n',
                 'xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx6xxxxxxxxxxxxxx9xxxxxxxxxxxxx3xxx9xxxxxxxxxxxxxxxx0xxxxxxxxxxxxxxxxx2xxxx2xxx6xxxxx/xx54xxxxxxxxx4xxx3xxxxxx9xx3xxxxx39xxxxxxxxx5xx91xxxx7xxxxxx8xxxxxxxxxxxxxxxx9xxx93xxxxxxxxxxxxxxxxx7xxx8xx8xx4/x1xxxxx1x3xxxxxxxxxxxxx3xxxxxx9xx4xx4x7xxxxxxxxxxxxx1xxxxxxxxx7xxxxxxxxxxxxxx4xx6xxxxxxxxx9xxx7xxxx2xxxxxxxxxxxxxxxxxxxxxx8xxxxxxxxxxxxxxxxxxxx6xx== xxxxx010 xxxxxxxxxx\n']
}

def foo():
    xxx_xxx = (
        'xxxx xxx xxxxxxxx_xxxx xx "xxxxxxxxxx".'
        '\n xxx: xxxxxx xxxxxxxx_xxxx=xxxxxxxxxx'
    ) # xxxx xxxxxxxxxx xxxx xx xxxx xx xxx xxxxxxxx xxxxxx xxxxx.

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
    (
        "This is a really long string inside of a print statement with extra arguments"
        " attached at the end of it."
    ),
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
        " dictionary. It is %s bad (#%d)."
    )
    % ("soooo", 2),
}

func_with_keywords(
    my_arg,
    my_kwarg=(
        "Long keyword strings also need to be wrapped, but they will probably need to"
        " be handled a little bit differently."
    ),
)

bad_split1 = (
    "But what should happen when code has already been formatted but in the wrong way?"
    " Like with a space at the beginning instead of the end. Or what about when it is"
    " split too soon?"
)

bad_split2 = (
    "But what should happen when code has already "
    "been formatted but in the wrong way? Like "
    "with a space at the beginning instead of the "
    "end. Or what about when it is split too "
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
    (
        "But what should happen when code has already "
        "been formatted but in the wrong way? Like "
        "with a space at the beginning instead of the "
        "end. Or what about when it is split too "
        "soon? In the case of a split that is too "
        "short, black will try to honer the custom "
        "split."
    ),
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
        " way? Like with a space at the beginning instead of the end. Or what about"
        " when it is split too soon?"
    ),
)

bad_split_func3(
    (
        "But what should happen when code has already "
        r"been formatted but in the wrong way? Like "
        "with a space at the beginning instead of the "
        r"end. Or what about when it is split too "
        r"soon? In the case of a split that is too "
        "short, black will try to honer the custom "
        "split."
    ),
    xxx,
    yyy,
    zzz,
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
    " must also be preserved, since some %s still uses it."
    % ("formatting", "code")
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
    " black. But boy they sure are handy. The problem is that some lines will need to"
    f" have the 'f' whereas others do not. This {line}, for example, needs one."
)

comment_string = (  # This comment gets thrown to the top.
    "Long lines with inline comments should have their comments appended to the"
    " reformatted string's enclosing right parentheses."
)

arg_comment_string = print(
    (  # This comment gets thrown to the top.
        "Long lines with inline comments which are apart of (and not the only member"
        " of) an argument list should have their comments appended to the reformatted"
        " string's enclosing left parentheses."
    ),
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
    " the AssertionError exception, which uses dynamic string %s."
    % "formatting"
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
    (
        "With a reallly generic name and with a really really long string that is, at"
        " some point down the line, "
        + added
        + " to a variable and then added to another string. But then what happens when"
        " the final string is also supppppperrrrr long?! Well then that second"
        " (realllllllly long) string should be split too."
    ),
    "and a second argument",
    and_a_third,
)

return (
    "A really really really really really really really really really really really"
    " really really long {} {}".format("return", "value")
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there."
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there."  # comment after comma
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there."
)

func_with_bad_comma(
    "This is a really long string argument to a function that has a trailing comma"
    " which should NOT be there."  # comment after comma
)

func_with_bad_parens(
    "short string that should have parens stripped", x, y, z,
)

func_with_bad_parens(
    x, y, "short string that should have parens stripped", z,
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

########## REGRESSION TESTS ##########
# There was a bug where tuples were being identified as long strings.
long_tuple = (
    "Apple",
    "Berry",
    "Cherry",
    "Dill",
    "Evergreen",
    "Fig",
    "Grape",
    "Harry",
    "Iglu",
    "Jaguar",
)

stupid_format_method_bug = (
    "Some really long string that just so happens to be the {} {} to force the 'format'"
    " method to hang over the line length boundary. This is pretty annoying."
    .format("perfect", "length")
)


class A:
    def foo():
        os.system(
            "This is a regression test. xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx"
            " xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx"
            " xxxx.".format("xxxxxxxxxx", "xxxxxx", "xxxxxxxxxx")
        )


class A:
    def foo():
        XXXXXXXXXXXX.append(
            (
                (
                    "xxx_xxxxxxxxxx(xxxxx={}, xxxx={}, xxxxx, xxxx_xxxx_xxxxxxxxxx={})"
                    .format(xxxxx, xxxx, xxxx_xxxx_xxxxxxxxxx)
                ),
                my_var,
                my_other_var,
            )
        )


class A:
    class B:
        def foo():
            bar(
                (
                    "[{}]: xxx_xxxxxxxxxx(xxxxx={}, xxxx={}, xxxxx={}"
                    " xxxx_xxxx_xxxxxxxxxx={}, xxxx={})"
                    .format(
                        xxxx._xxxxxxxxxxxxxx, xxxxx, xxxx, xxxx_xxxx_xxxxxxxxxx, xxxxxxx
                    )
                ),
                varX,
                varY,
                varZ,
            )


def foo(xxxx):
    for (xxx_xxxx, _xxx_xxx, _xxx_xxxxx, xxx_xxxx) in xxxx:
        for xxx in xxx_xxxx:
            assert ("x" in xxx) or (xxx in xxx_xxx_xxxxx), (
                "{0} xxxxxxx xx {1}, xxx {1} xx xxx xx xxxx xx xxx xxxx: xxx xxxx {2}"
                .format(xxx_xxxx, xxx, xxxxxx.xxxxxxx(xxx_xxx_xxxxx))
            )


class A:
    def disappearing_comment():
        return (
            (  # xx -x xxxxxxx xx xxx xxxxxxx.
                "{{xxx_xxxxxxxxxx_xxxxxxxx}} xxx xxxx {} {{xxxx}} >&2".format(
                    "{xxxx} {xxxxxx}"
                    if xxxxx.xx_xxxxxxxxxx
                    else (  # Disappearing Comment
                        "--xxxxxxx --xxxxxx=x --xxxxxx-xxxxx=xxxxxx"
                        " --xxxxxx-xxxx=xxxxxxxxxxx.xxx"
                    )
                )
            ),
            (x, y, z),
        )


class A:
    class B:
        def foo():
            xxxxx_xxxx(
                xx,
                (
                    "\t"
                    "@xxxxxx '{xxxx_xxx}\t' > {xxxxxx_xxxx}.xxxxxxx;"
                    "{xxxx_xxx} >> {xxxxxx_xxxx}.xxxxxxx 2>&1; xx=$$?;"
                    "xxxx $$xx"
                    .format(
                        xxxx_xxx=xxxx_xxxxxxx,
                        xxxxxx_xxxx=xxxxxxx + "/" + xxxx_xxx_xxxx,
                        x=xxx_xxxxx_xxxxx_xxx,
                    )
                ),
                x,
                y,
                z,
            )


func_call_where_string_arg_has_method_call_and_bad_parens(
    "A long string with {}. This string is so long that it is ridiculous. It can't fit"
    " on one line at alllll.".format("formatting")
)

func_call_where_string_arg_has_old_fmt_and_bad_parens(
    "A long string with {}. This string is so long that it is ridiculous. It can't fit"
    " on one line at alllll."
    % "formatting"
)

func_call_where_string_arg_has_old_fmt_and_bad_parens(
    "A long string with {}. This {} is so long that it is ridiculous. It can't fit on"
    " one line at alllll."
    % ("formatting", "string")
)


class A:
    def append(self):
        if True:
            xxxx.xxxxxxx.xxxxx(
                "xxxxxxxxxx xxxx xx xxxxxx(%x) xx %x xxxx xx xxx %x.xx"
                % (len(self) + 1, xxxx.xxxxxxxxxx, xxxx.xxxxxxxxxx)
                + " %.3f (%s) to %.3f (%s).\n"
                % (
                    xxxx.xxxxxxxxx,
                    xxxx.xxxxxxxxxxxxxx(xxxx.xxxxxxxxx),
                    x,
                    xxxx.xxxxxxxxxxxxxx(xx),
                )
            )


class A:
    def foo():
        some_func_call(
            "xxxxxxxxxx",
            (
                "xx {xxxxxxxxxxx}/xxxxxxxxxxx.xxx xxxx.xxx && xxxxxx -x "
                '"xxxx xxxxxxx xxxxxx xxxx; xxxx xxxxxx_xxxxx xxxxxx xxxx; '
                "xxxx.xxxx_xxxxxx(['xxxx.xxx'], xxxx.xxxxxxx().xxxxxxxxxx)\" "
            ),
            None,
            ("xxxxxxxxxxx",),
        ),


class A:
    def foo():
        some_func_call(
            (
                "xx {xxxxxxxxxxx}/xxxxxxxxxxx.xxx xxxx.xxx && xxxxxx -x "
                "xxxx, ('xxxxxxx xxxxxx xxxx, xxxx') xxxxxx_xxxxx xxxxxx xxxx; "
                "xxxx.xxxx_xxxxxx(['xxxx.xxx'], xxxx.xxxxxxx().xxxxxxxxxx)\" "
            ),
            None,
            ("xxxxxxxxxxx",),
        ),


xxxxxxx = {
    "xx": (
        "xxxx xxxxxxx xxxxxxxxx -x xxx -x /xxx/{0} -x xxx,xxx -xx {1} -xx {1} -xx"
        " xxx=xxx_xxxx,xxx_xx,xxx_xxx,xxx_xxxx,xxx_xx,xxx_xxx | xxxxxx -x xxxxxxxx -x"
        " xxxxxxxx -x"
    ),
    "xx": (
        "xxxx xxxxxxx xxxxxxxxx -x xxx -x /xxx/{0} -x xxx,xxx -xx {1} -xx {1} -xx xxx=xxx_xxxx_xxx_xxxx,xxx_xx_xxx_xxxx,xxx_xxxx_xxx_xxxx,xxx_xx_xxxx_xxxx,xxx_xxx_xxxx,xxx_xxx_xxxx xxxx=xxx | xxxxxx -x xxxxxxxx -x xxxxxxxx -x"
    ),
}


class A:
    def foo(self):
        if True:
            xxxxx_xxxxxxxxxxxx(
                "xxx xxxxxx xxx xxxxxxxxx.xx xx xxxxxxxx.  xxx xxxxxxxxxxxxx.xx"
                " xxxxxxx "
                + "xx xxxxxx xxxxxx xxxxxx xx xxxxxxx xxx xxx ${0} xx x xxxxxxxx xxxxx"
                .xxxxxx(xxxxxx_xxxxxx_xxx)
            )


class A:
    class B:
        def foo():
            row = {
                "xxxxxxxxxxxxxxx": xxxxxx_xxxxx_xxxx,
                # 'xxxxxxxxxxxxxxxxxxxxxxx'
                # 'xxxxxxxxxxxxxxxxxxxxxx'
                # 'xxxxxxxxxxxxxxxxxx'
                # 'xxxxxxxxxxxxxxxxx'
                "xxxxxxxxxx": xxxxx_xxxxx,
            }


class A:
    def xxxx_xxx_xx_xxxxxxxxxx_xxxx_xxxxxxxxx(xxxx):
        xxxxxxxx = [
            xxxxxxxxxxxxxxxx(
                "xxxx",
                xxxxxxxxxxx={"xxxx": 1.0,},
                xxxxxx={"xxxxxx 1": xxxxxx(xxxx="xxxxxx 1", xxxxxx=600.0)},
                xxxxxxxx_xxxxxxx=0.0,
            ),
            xxxxxxxxxxxxxxxx(
                "xxxxxxx",
                xxxxxxxxxxx={"xxxx": 1.0,},
                xxxxxx={"xxxxxx 1": xxxxxx(xxxx="xxxxxx 1", xxxxxx=200.0)},
                xxxxxxxx_xxxxxxx=0.0,
            ),
            xxxxxxxxxxxxxxxx("xxxx"),
        ]


some_dictionary = {
    "xxxxx006": [
        (
            "xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx0xx6xxxxxxxxxx2xxxxxx9xxxxxxxxxx0xxxxx1xxx2x/xx9xx6+x+xxxxxxxxxxxxxx4xxxxxxxxxxxxxxxxxxxxx43xxx2xx2x4x++xxx6xxxxxxxxx+xxxxx/xx9x+xxxxxxxxxxxxxx8x15xxxxxxxxxxxxxxxxx82xx/xxxxxxxxxxxxxx/x5xxxxxxxxxxxxxx6xxxxxx74x4/xxx4x+xxxxxxxxx2xxxxxxxx87xxxxx4xxxxxxxx3xx0xxxxx4xxx1xx9xx5xxxxxxx/xxxxx5xx6xx4xxxx1x/x2xxxxxxxxxxxx64xxxxxxx1x0xx5xxxxxxxxxxxxxx== xxxxx000 xxxxxxxxxx\n"
        ),
        (
            "xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx6xxxxxxxxxxxxxx9xxxxxxxxxxxxx3xxx9xxxxxxxxxxxxxxxx0xxxxxxxxxxxxxxxxx2xxxx2xxx6xxxxx/xx54xxxxxxxxx4xxx3xxxxxx9xx3xxxxx39xxxxxxxxx5xx91xxxx7xxxxxx8xxxxxxxxxxxxxxxx9xxx93xxxxxxxxxxxxxxxxx7xxx8xx8xx4/x1xxxxx1x3xxxxxxxxxxxxx3xxxxxx9xx4xx4x7xxxxxxxxxxxxx1xxxxxxxxx7xxxxxxxxxxxxxx4xx6xxxxxxxxx9xxx7xxxx2xxxxxxxxxxxxxxxxxxxxxx8xxxxxxxxxxxxxxxxxxxx6xx== xxxxx010 xxxxxxxxxx\n"
        ),
    ],
    "xxxxx016": [
        (
            "xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx0xx6xxxxxxxxxx2xxxxxx9xxxxxxxxxx0xxxxx1xxx2x/xx9xx6+x+xxxxxxxxxxxxxx4xxxxxxxxxxxxxxxxxxxxx43xxx2xx2x4x++xxx6xxxxxxxxx+xxxxx/xx9x+xxxxxxxxxxxxxx8x15xxxxxxxxxxxxxxxxx82xx/xxxxxxxxxxxxxx/x5xxxxxxxxxxxxxx6xxxxxx74x4/xxx4x+xxxxxxxxx2xxxxxxxx87xxxxx4xxxxxxxx3xx0xxxxx4xxx1xx9xx5xxxxxxx/xxxxx5xx6xx4xxxx1x/x2xxxxxxxxxxxx64xxxxxxx1x0xx5xxxxxxxxxxxxxx== xxxxx000 xxxxxxxxxx\n"
        ),
        (
            "xxx-xxx xxxxx3xxxx1xx2xxxxxxxxxxxxxx6xxxxxxxxxxxxxx9xxxxxxxxxxxxx3xxx9xxxxxxxxxxxxxxxx0xxxxxxxxxxxxxxxxx2xxxx2xxx6xxxxx/xx54xxxxxxxxx4xxx3xxxxxx9xx3xxxxx39xxxxxxxxx5xx91xxxx7xxxxxx8xxxxxxxxxxxxxxxx9xxx93xxxxxxxxxxxxxxxxx7xxx8xx8xx4/x1xxxxx1x3xxxxxxxxxxxxx3xxxxxx9xx4xx4x7xxxxxxxxxxxxx1xxxxxxxxx7xxxxxxxxxxxxxx4xx6xxxxxxxxx9xxx7xxxx2xxxxxxxxxxxxxxxxxxxxxx8xxxxxxxxxxxxxxxxxxxx6xx== xxxxx010 xxxxxxxxxx\n"
        ),
    ],
}


def foo():
    xxx_xxx = (  # xxxx xxxxxxxxxx xxxx xx xxxx xx xxx xxxxxxxx xxxxxx xxxxx.
        'xxxx xxx xxxxxxxx_xxxx xx "xxxxxxxxxx".\n xxx: xxxxxx xxxxxxxx_xxxx=xxxxxxxxxx'
    )
