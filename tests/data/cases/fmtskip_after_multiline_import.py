# `# fmt: skip` on the closing parenthesis line of a multi-line `from` import that
# is followed by another statement. The whole import is left alone.
from a import (
    b,
); import c  # fmt: skip

from d import (
    e  as  f,
    g,
); h  =  1  # fmt: skip
i  =  2


def foo():
    j  =  3
    from k import (
        l,
    ); from m import n  # fmt: skip

# output
# `# fmt: skip` on the closing parenthesis line of a multi-line `from` import that
# is followed by another statement. The whole import is left alone.
from a import (
    b,
); import c  # fmt: skip

from d import (
    e  as  f,
    g,
); h  =  1  # fmt: skip
i = 2


def foo():
    j = 3
    from k import (
        l,
    ); from m import n  # fmt: skip
