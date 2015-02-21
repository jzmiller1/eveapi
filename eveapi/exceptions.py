class Error(Exception):

    def __init__(self, code, message):
        self.code = code
        self.args = (message.rstrip("."),)

    def __unicode__(self):
        return '%s [code=%s]' % (self.args[0], self.code)


class RequestError(Error):
    pass


class AuthenticationError(Error):
    pass


class ServerError(Error):
    pass
