from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent  # NOT DRY
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent as component  # DRY
)

# Please keep __all__ alphabetized within each category.

__all__ = [
    # Super-special typing primitives.
    'Any',
    'Callable',
    'ClassVar',

    # ABCs (from collections.abc).
    'AbstractSet',  # collections.abc.Set.
    'ByteString',
    'Container',

    # Concrete collection types.
    'Counter',
    'Deque',
    'Dict',
    'DefaultDict',
    'List',
    'Set',
    'FrozenSet',
    'NamedTuple',  # Not really a type.
    'Generator',
]

not_shareables = [
    # singletons
    True,
    False,
    NotImplemented, ...,
    # builtin types and objects
    type,
    object,
    object(),
    Exception(),
    42,
    100.0,
    "spam",
    # user-defined types and objects
    Cheese,
    Cheese("Wensleydale"),
    SubBytes(b"spam"),
]

if 'PYTHON' in os.environ:
    add_compiler(compiler_from_env())
else:
    # for compiler in compilers.values():
         # add_compiler(compiler)
    add_compiler(compilers[(7.0, 32)])
    # add_compiler(compilers[(7.1, 64)])

# Comment before function.
def inline_comments_in_brackets_ruin_everything():
    if typedargslist:
        parameters.children = [
            children[0],  # (1
            body,
            children[-1]  # )1
        ]
        parameters.children = [
            children[0],
            body,
            children[-1],  # type: ignore
        ]
    else:
        parameters.children = [
            parameters.children[0],  # (2 what if this was actually long
            body,
            parameters.children[-1],  # )2
        ]
        parameters.children = [parameters.what_if_this_was_actually_long.children[0], body, parameters.children[-1]]  # type: ignore
    if (self._proc is not None
            # has the child process finished?
            and self._returncode is None
            # the child process has finished, but the
            # transport hasn't been notified yet?
            and self._proc.poll() is None):
        pass
    # no newline before or after
    short = [
     # one
     1,
     # two
     2]

    # no newline after
    call(arg1, arg2, """
short
""", arg3=True)

    ############################################################################

    call2(
    #short
    arg1,
    #but
    arg2,
    #multiline
    """
short
""",
    # yup
    arg3=True)
    lcomp = [
        element  # yup
        for element in collection  # yup
        if element is not None  # right
    ]
    lcomp2 = [
        # hello
        element
        # yup
        for element in collection
        # right
        if element is not None
    ]
    lcomp3 = [
        # This one is actually too long to fit in a single line.
        element.split('\n', 1)[0]
        # yup
        for element in collection.select_elements()
        # right
        if element is not None
    ]
    while True:
        if False:
            continue

            # and round and round we go
        # and round and round we go

   # let's return
    return Node(
        syms.simple_stmt,
        [
            Node(statement, result),
            Leaf(token.NEWLINE, '\n')  # FIXME: \r\n?
        ],
    )

CONFIG_FILES = [CONFIG_FILE, ] + SHARED_CONFIG_FILES + USER_CONFIG_FILES  # type: Final

class Test:
    def _init_host(self, parsed) -> None:
        if (parsed.hostname is None or  # type: ignore
                not parsed.hostname.strip()):
            pass

#######################
### SECTION COMMENT ###
#######################


instruction()#comment with bad spacing

# END COMMENTS
# MORE END COMMENTS


# output


from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent,  # NOT DRY
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent as component,  # DRY
)

# Please keep __all__ alphabetized within each category.

__all__ = [
    # Super-special typing primitives.
    "Any",
    "Callable",
    "ClassVar",
    # ABCs (from collections.abc).
    "AbstractSet",  # collections.abc.Set.
    "ByteString",
    "Container",
    # Concrete collection types.
    "Counter",
    "Deque",
    "Dict",
    "DefaultDict",
    "List",
    "Set",
    "FrozenSet",
    "NamedTuple",  # Not really a type.
    "Generator",
]

not_shareables = [
    # singletons
    True,
    False,
    NotImplemented,
    ...,
    # builtin types and objects
    type,
    object,
    object(),
    Exception(),
    42,
    100.0,
    "spam",
    # user-defined types and objects
    Cheese,
    Cheese("Wensleydale"),
    SubBytes(b"spam"),
]

if "PYTHON" in os.environ:
    add_compiler(compiler_from_env())
else:
    # for compiler in compilers.values():
    # add_compiler(compiler)
    add_compiler(compilers[(7.0, 32)])
    # add_compiler(compilers[(7.1, 64)])

# Comment before function.
def inline_comments_in_brackets_ruin_everything():
    if typedargslist:
        parameters.children = [children[0], body, children[-1]]  # (1  # )1
        parameters.children = [
            children[0],
            body,
            children[-1],  # type: ignore
        ]
    else:
        parameters.children = [
            parameters.children[0],  # (2 what if this was actually long
            body,
            parameters.children[-1],  # )2
        ]
        parameters.children = [parameters.what_if_this_was_actually_long.children[0], body, parameters.children[-1]]  # type: ignore
    if (
        self._proc is not None
        # has the child process finished?
        and self._returncode is None
        # the child process has finished, but the
        # transport hasn't been notified yet?
        and self._proc.poll() is None
    ):
        pass
    # no newline before or after
    short = [
        # one
        1,
        # two
        2,
    ]

    # no newline after
    call(
        arg1,
        arg2,
        """
short
""",
        arg3=True,
    )

    ############################################################################

    call2(
        # short
        arg1,
        # but
        arg2,
        # multiline
        """
short
""",
        # yup
        arg3=True,
    )
    lcomp = [
        element for element in collection if element is not None  # yup  # yup  # right
    ]
    lcomp2 = [
        # hello
        element
        # yup
        for element in collection
        # right
        if element is not None
    ]
    lcomp3 = [
        # This one is actually too long to fit in a single line.
        element.split("\n", 1)[0]
        # yup
        for element in collection.select_elements()
        # right
        if element is not None
    ]
    while True:
        if False:
            continue

            # and round and round we go
        # and round and round we go

    # let's return
    return Node(
        syms.simple_stmt,
        [Node(statement, result), Leaf(token.NEWLINE, "\n")],  # FIXME: \r\n?
    )


CONFIG_FILES = (
    [
        CONFIG_FILE,
    ]
    + SHARED_CONFIG_FILES
    + USER_CONFIG_FILES
)  # type: Final


class Test:
    def _init_host(self, parsed) -> None:
        if parsed.hostname is None or not parsed.hostname.strip():  # type: ignore
            pass


#######################
### SECTION COMMENT ###
#######################


instruction()  # comment with bad spacing

# END COMMENTS
# MORE END COMMENTS
