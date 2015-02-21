import copy


class Element(object):
    # Element is a namespace for attributes and nested tags
    def __str__(self):
        return "<Element '%s'>" % self._name

_fmt = u"%s:%s".__mod__


class Row(object):
    # A Row is a single database record associated with a Rowset.
    # The fields in the record are accessed as attributes by their respective
    # column name.
    #
    # To conserve resources, Row objects are only created on-demand. This is
    # typically done by Rowsets (e.g. when iterating over the rowset).

    def __init__(self, cols=None, row=None):
        self._cols = cols or []
        self._row = row or []

    def __nonzero__(self):
        return True

    def __ne__(self, other):
        return self.__cmp__(other)

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __cmp__(self, other):
        if type(other) != type(self):
            raise TypeError("Incompatible comparison type")
        return cmp(self._cols, other._cols) or cmp(self._row, other._row)

    def __hasattr__(self, this):
        if this in self._cols:
            return self._cols.index(this) < len(self._row)
        return False

    __contains__ = __hasattr__

    def get(self, this, default=None):
        if (this in self._cols) and (self._cols.index(this) < len(self._row)):
            return self._row[self._cols.index(this)]
        return default

    def __getattr__(self, this):
        try:
            return self._row[self._cols.index(this)]
        except:
            raise AttributeError(this)

    def __getitem__(self, this):
        return self._row[self._cols.index(this)]

    def __str__(self):
        return "Row(" + ','.join(map(_fmt, zip(self._cols, self._row))) + ")"


class Rowset(object):
    """
    Rowsets are collections of Row objects.

    Rowsets support most of the list interface:
      iteration, indexing and slicing

    As well as the following methods:

      IndexedBy(column)
        Returns an IndexRowset keyed on given column. Requires the column to
        be usable as primary key.

      GroupedBy(column)
        Returns a FilterRowset keyed on given column. FilterRowset objects
        can be accessed like dicts. See FilterRowset class below.

      SortBy(column, reverse=True)
        Sorts rowset in-place on given column. for a descending sort,
        specify reversed=True.

      SortedBy(column, reverse=True)
        Same as SortBy, except this returns a new rowset object instead of
        sorting in-place.

      Select(columns, row=False)
        Yields a column values tuple (value, ...) for each row in the rowset.
        If only one column is requested, then just the column value is
        provided instead of the values tuple.
        When row=True, each result will be decorated with the entire row.
    """

    def IndexedBy(self, column):
        return IndexRowset(self._cols, self._rows, column)

    def GroupedBy(self, column):
        return FilterRowset(self._cols, self._rows, column)

    def SortBy(self, column, reverse=False):
        ix = self._cols.index(column)
        self.sort(key=lambda e: e[ix], reverse=reverse)

    def SortedBy(self, column, reverse=False):
        rs = self[:]
        rs.SortBy(column, reverse)
        return rs

    def Select(self, *columns, **options):
        if len(columns) == 1:
            i = self._cols.index(columns[0])
            if options.get("row", False):
                for line in self._rows:
                    yield (line, line[i])
            else:
                for line in self._rows:
                    yield line[i]
        else:
            i = map(self._cols.index, columns)
            if options.get("row", False):
                for line in self._rows:
                    yield line, [line[x] for x in i]
            else:
                for line in self._rows:
                    yield [line[x] for x in i]

    def __init__(self, cols=None, rows=None):
        self._cols = cols or []
        self._rows = rows or []

    def append(self, row):
        if isinstance(row, list):
            self._rows.append(row)
        elif isinstance(row, Row) and len(row._cols) == len(self._cols):
            self._rows.append(row._row)
        else:
            raise TypeError("incompatible row type")

    def __add__(self, other):
        if isinstance(other, Rowset):
            if len(other._cols) == len(self._cols):
                self._rows += other._rows
        raise TypeError("rowset instance expected")

    def __nonzero__(self):
        return not not self._rows

    def __len__(self):
        return len(self._rows)

    def copy(self):
        return self[:]

    def __getitem__(self, ix):
        if type(ix) is slice:
            return Rowset(self._cols, self._rows[ix])
        return Row(self._cols, self._rows[ix])

    def sort(self, *args, **kw):
        self._rows.sort(*args, **kw)

    def __str__(self):
        return ("Rowset(columns=[%s], rows=%d)" % (','.join(self._cols), len(self)))

    def __getstate__(self):
        return (self._cols, self._rows)

    def __setstate__(self, state):
        self._cols, self._rows = state


class IndexRowset(Rowset):
    """
    An IndexRowset is a Rowset that keeps an index on a column.

    The interface is the same as Rowset, but provides an additional method:

      Get(key [, default])
        Returns the Row mapped to provided key in the index. If there is no
        such key in the index, KeyError is raised unless a default value was
        specified.
    """

    def Get(self, key, *default):
        row = self._items.get(key, None)
        if row is None:
            if default:
                return default[0]
            raise KeyError(key)
        return Row(self._cols, row)

    def __init__(self, cols=None, rows=None, key=None):
        try:
            if "," in key:
                self._ki = ki = [cols.index(k) for k in key.split(",")]
                self.composite = True
            else:
                self._ki = ki = cols.index(key)
                self.composite = False
        except IndexError:
            raise ValueError("Rowset has no column %s" % key)

        Rowset.__init__(self, cols, rows)
        self._key = key

        if self.composite:
            self._items = dict((tuple([row[k] for k in ki]), row) for row in self._rows)
        else:
            self._items = dict((row[ki], row) for row in self._rows)

    def __getitem__(self, ix):
        if type(ix) is slice:
            return IndexRowset(self._cols, self._rows[ix], self._key)
        return Rowset.__getitem__(self, ix)

    def append(self, row):
        Rowset.append(self, row)
        if self.composite:
            self._items[tuple([row[k] for k in self._ki])] = row
        else:
            self._items[row[self._ki]] = row

    def __getstate__(self):
        return (Rowset.__getstate__(self), self._items, self._ki)

    def __setstate__(self, state):
        state, self._items, self._ki = state
        Rowset.__setstate__(self, state)


class FilterRowset(object):
    """
    A FilterRowset works much like an IndexRowset, with the following
    differences:
    - FilterRowsets are accessed much like dicts
    - Each key maps to a Rowset, containing only the rows where the value
      of the column this FilterRowset was made on matches the key.
    """

    def __init__(self, cols=None, rows=None, key=None, key2=None, dict=None):
        if dict is not None:
            self._items = items = dict
        elif cols is not None:
            self._items = items = {}

            idfield = cols.index(key)
            if not key2:
                for row in rows:
                    id = row[idfield]
                    if id in items:
                        items[id].append(row)
                    else:
                        items[id] = [row]
            else:
                idfield2 = cols.index(key2)
                for row in rows:
                    id = row[idfield]
                    if id in items:
                        items[id][row[idfield2]] = row
                    else:
                        items[id] = {row[idfield2]: row}

        self._cols = cols
        self.key = key
        self.key2 = key2
        self._bind()

    def _bind(self):
        items = self._items
        self.keys = items.keys
        self.iterkeys = items.iterkeys
        self.__contains__ = items.__contains__
        self.has_key = items.has_key
        self.__len__ = items.__len__
        self.__iter__ = items.__iter__

    def copy(self):
        return FilterRowset(self._cols[:], None, self.key, self.key2, dict=copy.deepcopy(self._items))

    def get(self, key, default=[]):
        try:
            return self[key]
        except KeyError:
            if default is []:
                raise
        return default

    def __getitem__(self, i):
        if self.key2:
            return IndexRowset(self._cols, None, self.key2, self._items.get(i, {}))

        return Rowset(self._cols, self._items.get(i))

    def __getstate__(self):
        return (self._cols, self._rows, self._items, self.key, self.key2)

    def __setstate__(self, state):
        self._cols, self._rows, self._items, self.key, self.key2 = state
        self._bind()
