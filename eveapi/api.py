import urlparse

from .context import _RootContext
from .parser import _autocast

proxy = None
proxySSL = False


def set_cast_func(func):
    """
    Sets an alternative value casting function for the XML parser.
    The function must have 2 arguments; key and value. It should return a
    value or object of the type appropriate for the given attribute name/key.
    func may be None and will cause the default _autocast function to be used.
    """
    global _castfunc
    _castfunc = _autocast if func is None else func


def set_user_agent(user_agent_string):
    """
    Sets a User-Agent for any requests sent by the library.
    """
    global USER_AGENT
    USER_AGENT = user_agent_string


def EVEAPIConnection(url="api.eveonline.com", cacheHandler=None, proxy=None, proxySSL=False):
    """
    Creates an API object through which you can call remote functions.

    The following optional arguments may be provided:

    url - root location of the EVEAPI server

    proxy - (host,port) specifying a proxy server through which to request
            the API pages. Specifying a proxy overrides default proxy.

    proxySSL - True if the proxy requires SSL, False otherwise.

    cacheHandler - an object which must support the following interface:

         retrieve(host, path, params)

             Called when eveapi wants to fetch a document.
             host is the address of the server, path is the full path to
             the requested document, and params is a dict containing the
             parameters passed to this api call (keyID, vCode, etc).
             The method MUST return one of the following types:

              None - if your cache did not contain this entry
              str/unicode - eveapi will parse this as XML
              Element - previously stored object as provided to store()
              file-like object - eveapi will read() XML from the stream.

         store(host, path, params, doc, obj)

             Called when eveapi wants you to cache this item.
             You can use obj to get the info about the object (cachedUntil
             and currentTime, etc) doc is the XML document the object
             was generated from. It's generally best to cache the XML, not
             the object, unless you pickle the object. Note that this method
             will only be called if you returned None in the retrieve() for
             this object.
    """

    if not url.startswith("http"):
        url = "https://" + url
    p = urlparse.urlparse(url, "https")
    if p.path and p.path[-1] == "/":
        p.path = p.path[:-1]
    ctx = _RootContext(None, p.path, {}, {})
    ctx._handler = cacheHandler
    ctx._scheme = p.scheme
    ctx._host = p.netloc
    ctx._proxy = proxy or globals()["proxy"]
    ctx._proxySSL = proxySSL or globals()["proxySSL"]
    return ctx
