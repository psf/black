import typing
from typing import List, Tuple

# We should not treat the trailing comma
# in a single-element tuple type as a magic comma.
a: tuple[int,]
b: Tuple[int,]
c: typing.Tuple[int,]

# The magic comma still applies to non tuple types.
d: list[int,]
e: List[int,]
f: typing.List[int,]

# output
import typing
from typing import List, Tuple

# We should not treat the trailing comma
# in a single-element tuple type as a magic comma.
a: tuple[int,]
b: Tuple[int,]
c: typing.Tuple[int,]

# The magic comma still applies to non tuple types.
d: list[
    int,
]
e: List[
    int,
]
f: typing.List[
    int,
]
