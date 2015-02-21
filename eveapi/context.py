import http.client
import urllib.request, urllib.parse, urllib.error
import warnings

from eveapi import DEFAULT_UA, USER_AGENT
from .exceptions import (
    AuthenticationError,
    Error,
    ServerError
)
from .parser import _ParseXML

_listtypes = (list, tuple, dict)


class _Context(object):

    def __init__(self, root, path, parentDict, newKeywords=None):
        self._root = root or self
        self._path = path
        if newKeywords:
            if parentDict:
                self.parameters = parentDict.copy()
            else:
                self.parameters = {}
            self.parameters.update(newKeywords)
        else:
            self.parameters = parentDict or {}

    def context(self, *args, **kw):
        if kw or args:
            path = self._path
            if args:
                path += "/" + "/".join(args)
            return self.__class__(self._root, path, self.parameters, kw)
        else:
            return self

    def __getattr__(self, this):
        # perform arcane attribute majick trick
        return _Context(self._root, self._path + "/" + this, self.parameters)

    def __call__(self, **kw):
        if kw:
            # specified keywords override contextual ones
            for k, v in self.parameters.items():
                if k not in kw:
                    kw[k] = v
        else:
            # no keywords provided, just update with contextual ones.
            kw.update(self.parameters)

        # now let the root context handle it further
        return self._root(self._path, **kw)


class _AuthContext(_Context):

    def character(self, characterID):
        # returns a copy of this connection object but for every call made
        # through it, it will add the folder "/char" to the url, and the
        # characterID to the parameters passed.
        return _Context(self._root, self._path + "/char", self.parameters, {"characterID": characterID})

    def corporation(self, characterID):
        # same as character except for the folder "/corp"
        return _Context(self._root, self._path + "/corp", self.parameters, {"characterID": characterID})


class _RootContext(_Context):

    def auth(self, **kw):
        if len(kw) == 2 and (("keyID" in kw and "vCode" in kw) or ("userID" in kw and "apiKey" in kw)):
            return _AuthContext(self._root, self._path, self.parameters, kw)
        raise ValueError("Must specify keyID and vCode")

    def setcachehandler(self, handler):
        self._root._handler = handler

    def __call__(self, path, **kw):
        # convert list type arguments to something the API likes
        for k, v in kw.items():
            if isinstance(v, _listtypes):
                kw[k] = ','.join(map(str, list(v)))

        cache = self._root._handler

        # now send the request
        path += ".xml.aspx"

        if cache:
            response = cache.retrieve(self._host, path, kw)
        else:
            response = None

        if response is None:
            if not USER_AGENT:
                warnings.warn("No User-Agent set! Please use the set_user_agent() module-level function before accessing the EVE API.", stacklevel=3)

            if self._proxy is None:
                req = path
                if self._scheme == "https":
                    conn = http.client.HTTPSConnection(self._host)
                else:
                    conn = http.client.HTTPConnection(self._host)
            else:
                req = self._scheme+'://'+self._host+path
                if self._proxySSL:
                    conn = http.client.HTTPSConnection(*self._proxy)
                else:
                    conn = http.client.HTTPConnection(*self._proxy)

            if kw:
                conn.request("POST", req, urllib.parse.urlencode(kw), {"Content-type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT or DEFAULT_UA})
            else:
                conn.request("GET", req, "", {"User-Agent": USER_AGENT or DEFAULT_UA})

            response = conn.getresponse()
            if response.status != 200:
                if response.status == http.client.NOT_FOUND:
                    raise AttributeError("'%s' not available on API server (404 Not Found)" % path)
                elif response.status == http.client.FORBIDDEN:
                    raise AuthenticationError(response.status, 'HTTP 403 - Forbidden')
                else:
                    raise ServerError(response.status, "'%s' request failed (%s)" % (path, response.reason))

            if cache:
                store = True
                response = response.read()
            else:
                store = False
        else:
            store = False

        retrieve_fallback = cache and getattr(cache, "retrieve_fallback", False)
        if retrieve_fallback:
            # implementor is handling fallbacks...
            try:
                return _ParseXML(response, True, store and (lambda obj: cache.store(self._host, path, kw, response, obj)))
            except Error as e:
                response = retrieve_fallback(self._host, path, kw, reason=e)
                if response is not None:
                    return response
                raise
        else:
            # implementor is not handling fallbacks...
            return _ParseXML(response, True, store and (lambda obj: cache.store(self._host, path, kw, response, obj)))
