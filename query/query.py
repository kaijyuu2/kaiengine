from collections import defaultdict
from weakref import WeakSet

query_dict = defaultdict(WeakSet)

def _addSource(key, source):
    query_dict[key].add(source)

def _removeSource(key, source):
    try:
        query_dict[key].remove(source)
    except KeyError:
        pass

def _removeAllSources(key):
    try:
        del query_dict[key]
    except KeyError:
        pass

def _purgeAllQueryData():
    global query_dict
    query_dict = defaultdict(WeakSet)

def _getData(key):
    return [source() for source in query_dict[key]]
