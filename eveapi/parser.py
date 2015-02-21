from datetime import datetime
from xml.parsers import expat

from .containers import (
    Element,
    IndexRowset,
    Rowset,
)
from .exceptions import (
    AuthenticationError,
    Error,
    RequestError,
    ServerError,
)


def _autocast(key, value):
    # attempts to cast an XML string to the most probable type.
    try:
        if value.strip("-").isdigit():
            return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if len(value) == 19 and value[10] == ' ':
        # it could be a date string
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except OverflowError:
            pass
        except ValueError:
            pass

    # couldn't cast. return string unchanged.
    return value

_castfunc = _autocast


def ParseXML(file_or_string):
    try:
        return _ParseXML(file_or_string, False, None)
    except TypeError:
        raise TypeError("XML data must be provided as string or file-like object")


def _ParseXML(response, fromContext, storeFunc):
    # pre/post-process XML or Element data

    if fromContext and isinstance(response, Element):
        obj = response
    elif type(response) in (str, str):
        obj = _Parser().Parse(response, False)
    elif hasattr(response, "read"):
        obj = _Parser().Parse(response, True)
    else:
        raise TypeError("retrieve method must return None, string, file-like object or an Element instance")

    error = getattr(obj, "error", False)
    if error:
        if error.code >= 500:
            raise ServerError(error.code, error.data)
        elif error.code >= 200:
            raise AuthenticationError(error.code, error.data)
        elif error.code >= 100:
            raise RequestError(error.code, error.data)
        else:
            raise Error(error.code, error.data)

    result = getattr(obj, "result", False)
    if not result:
        raise RuntimeError("API object does not contain result")

    if fromContext and storeFunc:
        # call the cache handler to store this object
        storeFunc(obj)

    # make metadata available to caller somehow
    result._meta = obj

    return result


class _Parser(object):

    def Parse(self, data, isStream=False):
        self.container = self.root = None
        self._cdata = False
        p = expat.ParserCreate()
        p.StartElementHandler = self.tag_start
        p.CharacterDataHandler = self.tag_cdata
        p.StartCdataSectionHandler = self.tag_cdatasection_enter
        p.EndCdataSectionHandler = self.tag_cdatasection_exit
        p.EndElementHandler = self.tag_end
        p.ordered_attributes = True
        p.buffer_text = True

        if isStream:
            p.ParseFile(data)
        else:
            p.Parse(data, True)
        return self.root

    def tag_cdatasection_enter(self):
        # encountered an explicit CDATA tag.
        self._cdata = True

    def tag_cdatasection_exit(self):
        if self._cdata:
            # explicit CDATA without actual data. expat doesn't seem
            # to trigger an event for this case, so do it manually.
            # (_cdata is set False by this call)
            self.tag_cdata("")
        else:
            self._cdata = False

    def tag_start(self, name, attributes):
        # <hack>
        # If there's a colon in the tag name, cut off the name from the colon
        # onward. This is a workaround to make certain bugged XML responses
        # (such as eve/CharacterID.xml.aspx) work.
        if ":" in name:
            name = name[:name.index(":")]
        # </hack>

        if name == "rowset":
            # for rowsets, use the given name
            try:
                columns = attributes[attributes.index('columns')+1].replace(" ", "").split(",")
            except ValueError:
                # rowset did not have columns tag set (this is a bug in API)
                # columns will be extracted from first row instead.
                columns = []

            try:
                priKey = attributes[attributes.index('key') + 1]
                this = IndexRowset(cols=columns, key=priKey)
            except ValueError:
                this = Rowset(cols=columns)

            this._name = attributes[attributes.index('name') + 1]
            this.__catch = "row"  # tag to auto-add to rowset.
        else:
            this = Element()
            this._name = name

        this.__parent = self.container

        if self.root is None:
            # We're at the root. The first tag has to be "eveapi" or we can't
            # really assume the rest of the xml is going to be what we expect.
            if name != "eveapi":
                raise RuntimeError("Invalid API response")
            try:
                this.version = attributes[attributes.index("version")+1]
            except KeyError:
                raise RuntimeError("Invalid API response")
            self.root = this

        if isinstance(self.container, Rowset) and (self.container.__catch == this._name):
            # <hack>
            # - check for missing columns attribute (see above).
            # - check for missing row attributes.
            # - check for extra attributes that were not defined in the rowset,
            #   such as rawQuantity in the assets lists.
            # In either case the tag is assumed to be correct and the rowset's
            # columns are overwritten with the tag's version, if required.
            numAttr = len(attributes) / 2
            numCols = len(self.container._cols)
            if numAttr < numCols and (attributes[-2] == self.container._cols[-1]):
                # the row data is missing attributes that were defined in the rowset.
                # missing attributes' values will be set to None.
                fixed = []
                row_idx = 0
                hdr_idx = 0
                numAttr *= 2

                for col in self.container._cols:
                    if col == attributes[row_idx]:
                        fixed.append(_castfunc(col, attributes[row_idx+1]))
                        row_idx += 2
                    else:
                        fixed.append(None)
                    hdr_idx += 1
                self.container.append(fixed)
            else:
                if not self.container._cols or (numAttr > numCols):
                    # the row data contains more attributes than were defined.
                    self.container._cols = attributes[0::2]
                self.container.append([_castfunc(attributes[i], attributes[i + 1]) for i in range(0, len(attributes), 2)])
            # </hack>

            this._isrow = True
            this._attributes = this._attributes2 = None
        else:
            this._isrow = False
            this._attributes = attributes
            this._attributes2 = []

        self.container = self._last = this
        self.has_cdata = False

    def tag_cdata(self, data):
        self.has_cdata = True
        if self._cdata:
            # unset cdata flag to indicate it's been handled.
            self._cdata = False
        else:
            if data in ("\r\n", "\n") or data.lstrip() != data:
                return

        this = self.container
        data = _castfunc(this._name, data)

        if this._isrow:
            # sigh. anonymous data inside rows makes Entity cry.
            # for the love of Jove, CCP, learn how to use rowsets.
            parent = this.__parent
            _row = parent._rows[-1]
            _row.append(data)
            if len(parent._cols) < len(_row):
                parent._cols.append("data")

        elif this._attributes:
            # this tag has attributes, so we can't simply assign the cdata
            # as an attribute to the parent tag, as we'll lose the current
            # tag's attributes then. instead, we'll assign the data as
            # attribute of this tag.
            this.data = data
        else:
            # this was a simple <tag>data</tag> without attributes.
            # we won't be doing anything with this actual tag so we can just
            # bind it to its parent (done by __tag_end)
            setattr(this.__parent, this._name, data)

    def tag_end(self, name):
        this = self.container

        if this is self.root:
            del this._attributes
            return

        # we're done with current tag, so we can pop it off. This means that
        # self.container will now point to the container of element 'this'.
        self.container = this.__parent
        del this.__parent

        attributes = this.__dict__.pop("_attributes")
        attributes2 = this.__dict__.pop("_attributes2")
        if attributes is None:
            # already processed this tag's closure early, in tag_start()
            return

        if self.container._isrow:
            # Special case here. tags inside a row! Such tags have to be
            # added as attributes of the row.
            parent = self.container.__parent

            # get the row line for this element from its parent rowset
            _row = parent._rows[-1]

            # add this tag's value to the end of the row
            _row.append(getattr(self.container, this._name, this))

            # fix columns if neccessary.
            if len(parent._cols) < len(_row):
                parent._cols.append(this._name)
        else:
            # see if there's already an attribute with this name (this shouldn't
            # really happen, but it doesn't hurt to handle this case!
            sibling = getattr(self.container, this._name, None)
            if sibling is None:
                if (not self.has_cdata) and (self._last is this) and (name != "rowset"):
                    if attributes:
                        # tag of the form <tag attribute=bla ... />
                        e = Element()
                        e._name = this._name
                        setattr(self.container, this._name, e)
                        for i in range(0, len(attributes), 2):
                            setattr(e, attributes[i], attributes[i+1])
                    else:
                        # tag of the form: <tag />, treat as empty string.
                        setattr(self.container, this._name, "")
                else:
                    self.container._attributes2.append(this._name)
                    setattr(self.container, this._name, this)

            # Note: there aren't supposed to be any NON-rowset tags containing
            # multiples of some tag or attribute. Code below handles this case.
            elif isinstance(sibling, Rowset):
                # its doppelganger is a rowset, append this as a row to that.
                row = [_castfunc(attributes[i], attributes[i+1]) for i in range(0, len(attributes), 2)]
                row.extend([getattr(this, col) for col in attributes2])
                sibling.append(row)
            elif isinstance(sibling, Element):
                # parent attribute is an element. This means we're dealing
                # with multiple of the same sub-tag. Change the attribute
                # into a Rowset, adding the sibling element and this one.
                rs = Rowset()
                rs.__catch = rs._name = this._name
                row = [_castfunc(attributes[i], attributes[i+1]) for i in range(0, len(attributes), 2)]+[getattr(this, col) for col in attributes2]
                rs.append(row)
                row = [getattr(sibling, attributes[i]) for i in range(0, len(attributes), 2)]+[getattr(sibling, col) for col in attributes2]
                rs.append(row)
                rs._cols = [attributes[i] for i in range(0, len(attributes), 2)]+[col for col in attributes2]
                setattr(self.container, this._name, rs)
            else:
                # something else must have set this attribute already.
                # (typically the <tag>data</tag> case in tag_data())
                pass

        # Now fix up the attributes and be done with it.
        for i in range(0, len(attributes), 2):
            this.__dict__[attributes[i]] = _castfunc(attributes[i], attributes[i+1])

        return
