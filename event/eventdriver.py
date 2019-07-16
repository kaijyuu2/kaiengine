#event stuff
import traceback

from .eventkeys import *
from .event import Event

from kaiengine.uidgen import generateUniqueID
from kaiengine.sDict import sDict

#driver data
listeners_dict = {}
query_listeners = {}

def _addListener(listeners_key, listener, priority):
    if not listeners_key in listeners_dict:
        listeners_dict[listeners_key] = sDict()
    listeners_dict[listeners_key].append(Event(listener, priority))

def _removeListener(listeners_key, listener):
    if not listeners_key in listeners_dict:
        return
    for key, val in listeners_dict[listeners_key].items():
        if val.listener == listener:
            del listeners_dict[listeners_key][key]
            break

def _clearListeners(listeners_key):
    try:
        del listeners_dict[listeners_key]
    except KeyError:
        pass

def _callEvent(listeners_key, *args, **kwargs):
    try: sorted_listeners = sorted(list(listeners_dict[listeners_key].items()), key = lambda pair: pair[1].get_priority(), reverse = True)
    except KeyError: return
    deletion = []
    for key, listener in sorted_listeners:
        breakflag = listener.call_listener(*args, **kwargs)
        if listener.delete_me:
            deletion.append(key)
        if breakflag:
            break
    for i in deletion:
        try:
            del listeners_dict[listeners_key][i]
        except KeyError: pass


#queries

def _addQueryListener(key, listener):
    _removeQueryListener(key)
    def query_event(newkey, *args, **kwargs):
        _callEvent(newkey, listener(*args, **kwargs)) #capture listener
    _addListener(key, query_event, 0)
    query_listeners[key] = query_event

def _removeQueryListener(key, listener = None): #listener unnecessary since it's a query
    try:
        _removeListener(key, query_listeners[key])
        del query_listeners[key]
    except KeyError: pass

def _callQuery(key, *args, **kwargs):
    newkey = generateUniqueID("_query_callback_")
    returnval = [kwargs.pop("query_default", None)] #hacky workaround for scoping reasons
    def query_callback(newval):
        returnval[0] = newval #capture returnval
    _addListener(newkey, query_callback, 0)
    _callEvent(key, newkey, *args, **kwargs)
    _clearListeners(newkey)
    return returnval[0]
