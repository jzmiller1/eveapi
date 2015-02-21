VERSION = '1.4'
DEFAULT_UA = "eveapi.py/{}".format(VERSION)
USER_AGENT = None

from .api import (
    EVEAPIConnection
)
from .exceptions import (
    AuthenticationError,
    Error,
    RequestError,
    ServerError,
)
