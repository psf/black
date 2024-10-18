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
