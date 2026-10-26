# flags: --minimum-version=3.10 --line-ranges=51-51
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The compound statement headers outside of the range follow a `# fmt: off` /
# `# fmt: on` block that only holds comments. They are kept as they are.
class A:
    x = 1

    # fmt: off
    # fmt: on
    def g( self ):
        return 2


def process(items):
    with open( "a" ) as f:
        pass
    # fmt: off
    # fmt: on
    with open( "b" ) as g:
        pass
    for item in items:
        handle(item)
    # fmt: off
    # TABLE = [1,   2,   3]
    # fmt: on
    while  pending():
        cleanup()
    if ready:
        pass
    # fmt: off
    # fmt: on
    else :
        wait()
    match command:
        case "a":
            pass
        # fmt: off
        # fmt: on
        case  "b":
            pass
    return  items


# fmt: off
# fmt: on

with open( "c" ) as h:
    pass
x  =  1

# output

# flags: --minimum-version=3.10 --line-ranges=51-51
# NOTE: If you need to modify this file, pay special attention to the --line-ranges=
# flag above as it's formatting specifically these lines.

# The compound statement headers outside of the range follow a `# fmt: off` /
# `# fmt: on` block that only holds comments. They are kept as they are.
class A:
    x = 1

    # fmt: off
    # fmt: on
    def g( self ):
        return 2


def process(items):
    with open( "a" ) as f:
        pass
    # fmt: off
    # fmt: on
    with open( "b" ) as g:
        pass
    for item in items:
        handle(item)
    # fmt: off
    # TABLE = [1,   2,   3]
    # fmt: on
    while  pending():
        cleanup()
    if ready:
        pass
    # fmt: off
    # fmt: on
    else :
        wait()
    match command:
        case "a":
            pass
        # fmt: off
        # fmt: on
        case  "b":
            pass
    return  items


# fmt: off
# fmt: on

with open( "c" ) as h:
    pass
x = 1
