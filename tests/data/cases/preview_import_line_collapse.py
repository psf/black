# flags: --preview
from middleman.authentication import validate_oauth_token


logger = logging.getLogger(__name__)


# case 2 comment after import
from middleman.authentication import validate_oauth_token
#comment

logger = logging.getLogger(__name__)


# case 3 comment after import
from middleman.authentication import validate_oauth_token
# comment
logger = logging.getLogger(__name__)


from middleman.authentication import validate_oauth_token



logger = logging.getLogger(__name__)


# case 4 try catch with import after import
import os
import os



try:
    import os
except Exception:
    pass

try:
    import os
    def func():
        a = 1
except Exception:
    pass


# case 5 multiple imports
import os
import os

import os
import os





for i in range(10):
    print(i)


# case 6 import in function
def func():
    print()
    import os
    def func():
        pass
    print()


def func():
    import os
    a = 1
    print()


def func():
    import os


    a = 1
    print()


def func():
    import os



    a = 1
    print()

# output


from middleman.authentication import validate_oauth_token

logger = logging.getLogger(__name__)


# case 2 comment after import
from middleman.authentication import validate_oauth_token

# comment

logger = logging.getLogger(__name__)


# case 3 comment after import
from middleman.authentication import validate_oauth_token

# comment
logger = logging.getLogger(__name__)


from middleman.authentication import validate_oauth_token

logger = logging.getLogger(__name__)


# case 4 try catch with import after import
import os
import os

try:
    import os
except Exception:
    pass

try:
    import os

    def func():
        a = 1

except Exception:
    pass


# case 5 multiple imports
import os
import os

import os
import os

for i in range(10):
    print(i)


# case 6 import in function
def func():
    print()
    import os

    def func():
        pass

    print()


def func():
    import os

    a = 1
    print()


def func():
    import os

    a = 1
    print()


def func():
    import os

    a = 1
    print()
