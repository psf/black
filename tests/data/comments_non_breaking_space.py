from .config import (  ConfigTypeAttributes,    Int,    Path,    # String,
    # DEFAULT_TYPE_ATTRIBUTES,
)

result = 1  # A simple comment with a NBSP
result = (    1, ) # Another NBSP

result = 1    # type: ignore
result = 1# This comment is talking about type: ignore and start with NBSP
square = Square(4) # type: Optional[Square]

def function(a:int=42):
    """ This docstring start with a NBSP
        There is one NBSP column 5 here
       This is 7 NBSP
    """

    #    There's a NBSP + 3 spaces before
    #    And 4 spaces on the next line
    pass

# output
from .config import (
    ConfigTypeAttributes,
    Int,
    Path,  # String,
    # DEFAULT_TYPE_ATTRIBUTES,
)

result = 1  # A simple comment
result = (1,)  # Another one

result = 1  #  type: ignore
result = 1  # This comment is talking about type: ignore
square = Square(4)  #  type: Optional[Square]


def function(a: int = 42):
    """This docstring is already formatted
    a
    b
    """
    #    There's a NBSP + 3 spaces before
    #    And 4 spaces on the next line
    pass
