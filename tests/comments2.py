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

def inline_comments_in_brackets_ruin_everything():
    if typedargslist:
        parameters.children = [
            parameters.children[0],  # (1
            body,
            parameters.children[-1],  # )1
        ]
    else:
        parameters.children = [
            parameters.children[0],  # (2 what if this was actually long
            body,
            parameters.children[-1],  # )2
        ]
    if (self._proc is not None
            # has the child process finished?
            and self._returncode is None
            # the child process has finished, but the
            # transport hasn't been notified yet?
            and self._proc.poll() is None):
        pass
    short = [
     # one
     1,
     # two
     2]
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
    return Node(
        syms.simple_stmt,
        [
            Node(statement, result),
            Leaf(token.NEWLINE, '\n'),  # FIXME: \r\n?
        ],
    )

instruction()

# END COMMENTS
# MORE END COMMENTS


# output


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


def inline_comments_in_brackets_ruin_everything():
    if typedargslist:
        parameters.children = [
            parameters.children[0], body, parameters.children[-1]  # (1  # )1
        ]
    else:
        parameters.children = [
            parameters.children[0],  # (2 what if this was actually long
            body,
            parameters.children[-1],  # )2
        ]
    if (
        self._proc is not None
        # has the child process finished?
        and self._returncode is None
        # the child process has finished, but the
        # transport hasn't been notified yet?
        and self._proc.poll() is None
    ):
        pass
    short = [
        # one
        1,
        # two
        2,
    ]
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
        element.split('\n', 1)[0]
        # yup
        for element in collection.select_elements()
        # right
        if element is not None
    ]
    return Node(
        syms.simple_stmt,
        [Node(statement, result), Leaf(token.NEWLINE, '\n')],  # FIXME: \r\n?
    )


instruction()
# END COMMENTS
# MORE END COMMENTS
