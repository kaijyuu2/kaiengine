# -*- coding: utf-8 -*-

from sortedcontainers import SortedDict
from kaiengine.uidgen import generateUniqueID
from kaiengine.sDict import sDict

from .delayedeventexception import DelayedEventException

_delayed_events = SortedDict()
_delayed_events_ids = {}
_currently_running_events = False

#please use this system very sparingly. Scheduling is almost always superior; this is for once per frame actions that collate a lot of data


def delay(listener, priority = 0, *args, **kwargs):
    if not _currently_running_events:
        try:
            priority = priority()
        except:
            pass
        newid = generateUniqueID("DELAY_EVENT")
        try:
            newkey = _delayed_events[priority].append(listener, args, kwargs, newid)
        except KeyError:
            _delayed_events[priority] = sDict()
            newkey = _delayed_events[priority].append(listener, args, kwargs, newid)
        _delayed_events_ids[newid] = (priority, newkey)
        return newid
    else:
        raise DelayedEventException("Cannot delay events in a delayed event")
    
def undelay(ID):
    try:
        priority, key = _delayed_events_ids[ID]
        _removeDelayEvent(priority, key)
    except KeyError:
        pass
    
def runDelayedEvents():
    global _currently_running_events
    _currently_running_events = True
    for priority, val in _delayed_events.items():
        listener, args, kwargs, ID = val
        try:
            listener(*args, **kwargs)
        except:
            import traceback
            from kaiengine.debug import debugMessage
            debugMessage("Error in delayed event.")
            traceback.print_exc()
    _removeAllDelayEvents()
    _currently_running_events = False
    
def _removeDelayEvent(priority, key):
    ID = None
    try:
        ID = _delayed_events[priority].pop(key)[3]
    except KeyError:
        pass
    _delayed_events_ids.pop(ID, None)
    
def _removeAllDelayEvents():
    _delayed_events.clear()
    _delayed_events_ids.clear()