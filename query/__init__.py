"""kaiengine.query
API for pulling data from arbitrary sources without ref issues.

Public methods:

    addSource(key, source):
        Register a callable as a data source for a key.

    removeSource(key, source):
        Remove a callable as a data source for a key.
        Harmless if it isn't one.

    removeAllSources(key):
        Remove all data sources associated with a key, if it has any.

    getData(key):
        Return a list of all values from data sources for a key.
        Order is not guaranteed in any way.

    purgeAllQueryData():
        Remove ALL associations of all data sources and keys.
        Might be useful to free memory if creating/discarding many keys.

Notes:

    Keys must be hashable and should normally be strings.

    Data sources must be callable.

    Sources that fall out of scope elsewhere will automatically be
    purged from the query system.

    If a sorted result is desired, incorporate this into the design
    of the replies and sort after receiving them.

"""

from kaiengine.query.query import _addSource as addSource
from kaiengine.query.query import _removeSource as removeSource
from kaiengine.query.query import _removeAllSources as removeAllSources
from kaiengine.query.query import _getData as getData
from kaiengine.query.query import _purgeAllQueryData as purgeAllQueryData
