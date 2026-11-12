# Compound statement headers with `# fmt: skip` right after a `# fmt: off` /
# `# fmt: on` block that only holds comments. They are kept as they are.

with open("a") as f:
    pass
# fmt: off
# fmt: on
with open( "b" ) as g:  # fmt: skip
    pass


def setup():
    connect()


# fmt: off
# TABLE = [1,   2,   3]
# fmt: on
if DEBUG :  # fmt: skip
    enable_tracing()


def process(items):
    for item in items:
        handle(item)
    # fmt: off
    # fmt: on
    while  pending():  # fmt: skip
        cleanup()


class A:
    def f(self):
        return 1

    # fmt: off
    # fmt: on
    def g( self ):  # fmt: skip
        return 2


try:
    pass
except ValueError:
    pass
# fmt: off
# fmt: on
# fmt: off
# fmt: on
if (  ready  ):  # fmt: skip
    pass


if ready:
    pass
# fmt: off
# fmt: on
elif  waiting:  # fmt: skip
    wait()
# fmt: off
# fmt: on
else :  # fmt: skip
    stop()


try:
    pass
# fmt: off
# fmt: on
finally :  # fmt: skip
    close()


@decorator
# fmt: off
# fmt: on
class  B:  # fmt: skip
    pass


# fmt: off
# fmt: on
if ready: start();  run()  # fmt: skip


match command:
    case "a":
        pass
    # fmt: off
    # fmt: on
    case  "b":  # fmt: skip
        pass
