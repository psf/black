"""cow
say""",
call(3, "dogsay", textwrap.dedent("""dove
    coo""" % "cowabunga"))
call(3, "dogsay", textwrap.dedent("""dove
coo""" % "cowabunga"))
call(3, textwrap.dedent("""cow
    moo""" % "cowabunga"), "dogsay")
call(3, "dogsay", textwrap.dedent("""crow
    caw""" % "cowabunga"),)
call(3, textwrap.dedent("""cat
    meow""" % "cowabunga"), {"dog", "say"})
call(3, {"dog", "say"}, textwrap.dedent("""horse
    neigh""" % "cowabunga"))
call(3, {"dog", "say"}, textwrap.dedent("""pig
    oink""" % "cowabunga"),)
textwrap.dedent("""A one-line triple-quoted string.""")
textwrap.dedent("""A two-line triple-quoted string
since it goes to the next line.""")
textwrap.dedent("""A three-line triple-quoted string
that not only goes to the next line
but also goes one line beyond.""")
textwrap.dedent("""\
    A triple-quoted string
    actually leveraging the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. file contents.
""")
path.write_text(textwrap.dedent("""\
    A triple-quoted string
    actually leveraging the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. file contents.
"""))
path.write_text(textwrap.dedent("""\
    A triple-quoted string
    actually leveraging the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. {config_filename} file contents.
""".format("config_filename", config_filename)))
# Another use case
data = yaml.load("""\
a: 1
b: 2
""")
data = yaml.load("""\
a: 1
b: 2
""",)
data = yaml.load(
    """\
    a: 1
    b: 2
"""
)

MULTILINE = """
foo
""".replace("\n", "")
generated_readme = lambda project_name: """
{}

<Add content here!>
""".strip().format(project_name)
parser.usage += """
Custom extra help summary.

Extra test:
- with
- bullets
"""


def get_stuff(cr, value):
    # original
    cr.execute("""
        SELECT whatever
          FROM some_table t
         WHERE id = %s
    """, [value])
    return cr.fetchone()


def get_stuff(cr, value):
    # preferred
    cr.execute(
        """
        SELECT whatever
          FROM some_table t
         WHERE id = %s
        """,
        [value],
    )
    return cr.fetchone()


call(arg1, arg2, """
short
""", arg3=True)
test_vectors = [
    "one-liner\n",
    "two\nliner\n",
    """expressed
as a three line
mulitline string""",
]

_wat = re.compile(
    r"""
    regex
    """,
    re.MULTILINE | re.VERBOSE,
)
dis_c_instance_method = """\
%3d           0 LOAD_FAST                1 (x)
              2 LOAD_CONST               1 (1)
              4 COMPARE_OP               2 (==)
              6 LOAD_FAST                0 (self)
              8 STORE_ATTR               0 (x)
             10 LOAD_CONST               0 (None)
             12 RETURN_VALUE
""" % (_C.__init__.__code__.co_firstlineno + 1,)
path.write_text(textwrap.dedent("""\
    A triple-quoted string
    actually {verb} the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. {file_type} file contents.
""".format(verb="using", file_type="test")))
{"""cow
moos"""}
["""cow
moos"""]
["""cow
moos""", """dog
woofs
and
barks"""]
def dastardly_default_value(
    cow: String = json.loads("""this
is
quite
the
dastadardly
value!"""),
    **kwargs,
):
    pass

print(f"""
    This {animal}
    moos and barks
{animal} say
""")
msg = f"""The arguments {bad_arguments} were passed in.
Please use `--build-option` instead,
`--global-option` is reserved to flags like `--verbose` or `--quiet`.
"""

# output
"""cow
say""",
call(
    3,
    "dogsay",
    textwrap.dedent("""dove
    coo""" % "cowabunga"),
)
call(
    3,
    "dogsay",
    textwrap.dedent("""dove
coo""" % "cowabunga"),
)
call(
    3,
    textwrap.dedent("""cow
    moo""" % "cowabunga"),
    "dogsay",
)
call(
    3,
    "dogsay",
    textwrap.dedent("""crow
    caw""" % "cowabunga"),
)
call(
    3,
    textwrap.dedent("""cat
    meow""" % "cowabunga"),
    {"dog", "say"},
)
call(
    3,
    {"dog", "say"},
    textwrap.dedent("""horse
    neigh""" % "cowabunga"),
)
call(
    3,
    {"dog", "say"},
    textwrap.dedent("""pig
    oink""" % "cowabunga"),
)
textwrap.dedent("""A one-line triple-quoted string.""")
textwrap.dedent("""A two-line triple-quoted string
since it goes to the next line.""")
textwrap.dedent("""A three-line triple-quoted string
that not only goes to the next line
but also goes one line beyond.""")
textwrap.dedent("""\
    A triple-quoted string
    actually leveraging the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. file contents.
""")
path.write_text(textwrap.dedent("""\
    A triple-quoted string
    actually leveraging the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. file contents.
"""))
path.write_text(textwrap.dedent("""\
    A triple-quoted string
    actually leveraging the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. {config_filename} file contents.
""".format("config_filename", config_filename)))
# Another use case
data = yaml.load("""\
a: 1
b: 2
""")
data = yaml.load(
    """\
a: 1
b: 2
""",
)
data = yaml.load("""\
    a: 1
    b: 2
""")

MULTILINE = """
foo
""".replace("\n", "")
generated_readme = lambda project_name: """
{}

<Add content here!>
""".strip().format(project_name)
parser.usage += """
Custom extra help summary.

Extra test:
- with
- bullets
"""


def get_stuff(cr, value):
    # original
    cr.execute(
        """
        SELECT whatever
          FROM some_table t
         WHERE id = %s
    """,
        [value],
    )
    return cr.fetchone()


def get_stuff(cr, value):
    # preferred
    cr.execute(
        """
        SELECT whatever
          FROM some_table t
         WHERE id = %s
        """,
        [value],
    )
    return cr.fetchone()


call(
    arg1,
    arg2,
    """
short
""",
    arg3=True,
)
test_vectors = [
    "one-liner\n",
    "two\nliner\n",
    """expressed
as a three line
mulitline string""",
]

_wat = re.compile(
    r"""
    regex
    """,
    re.MULTILINE | re.VERBOSE,
)
dis_c_instance_method = """\
%3d           0 LOAD_FAST                1 (x)
              2 LOAD_CONST               1 (1)
              4 COMPARE_OP               2 (==)
              6 LOAD_FAST                0 (self)
              8 STORE_ATTR               0 (x)
             10 LOAD_CONST               0 (None)
             12 RETURN_VALUE
""" % (_C.__init__.__code__.co_firstlineno + 1,)
path.write_text(textwrap.dedent("""\
    A triple-quoted string
    actually {verb} the textwrap.dedent functionality
    that ends in a trailing newline,
    representing e.g. {file_type} file contents.
""".format(verb="using", file_type="test")))
{"""cow
moos"""}
["""cow
moos"""]
[
    """cow
moos""",
    """dog
woofs
and
barks""",
]


def dastardly_default_value(
    cow: String = json.loads("""this
is
quite
the
dastadardly
value!"""),
    **kwargs,
):
    pass


print(f"""
    This {animal}
    moos and barks
{animal} say
""")
msg = f"""The arguments {bad_arguments} were passed in.
Please use `--build-option` instead,
`--global-option` is reserved to flags like `--verbose` or `--quiet`.
"""
