# Stubs for lib2to3.pgen2 (Python 3.6)

import os
import sys
from typing import Text, Union

if sys.version_info >= (3, 6):
    _Path = Union[Text, os.PathLike]
else:
    _Path = Text
