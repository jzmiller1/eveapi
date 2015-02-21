VERSION = '2.0'
DEFAULT_UA = "eveapi.py/{}".format(VERSION)
USER_AGENT = None

from .api import (
    Connect
)
from .exceptions import (
    AuthenticationError,
    Error,
    RequestError,
    ServerError,
)
