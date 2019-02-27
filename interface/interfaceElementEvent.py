from kaiengine.event import customEvent
from kaiengine.objectinterface import EventInterface
from kaiengine.uidgen import IdentifiedObject

from .interfaceElementKeys import *


def _event_response(event_key, priority=None, lock=False, sleep_when_unfocused=False):
    def decorator(func):
        func._listener_init_data = (event_key, priority, lock, sleep_when_unfocused)
        return func
    return decorator

def on_event(event_key, priority=None, lock=False):
    return _event_response(event_key, priority, lock)

def on_input(input_key, priority=None, lock=True):
    return _event_response(input_key, priority, lock, sleep_when_unfocused=True)

def _child_event_response(event_append, event_key, *args, **kwargs):
    if kwargs:
        try:
            priority = kwargs["priority"]
        except:
            priority = None
        try:
            lock = kwargs["lock"]
        except:
            lock = None
        def decorator(func):
            func._special_key_append = event_append
            func._child_listener_init_data = (event_key, priority, lock)
            return func
        return decorator
    else:
        func = args[0]
        func._special_key_append = event_append
        func._child_listener_init_data = (event_key, None, True) #TODO: consider whether we can make a better guess on lock value
    return func

def on_activate(*args, **kwargs):
    return _child_event_response(ACTIVATE_APPEND, EVENT_INTERFACE_ACTIVATED, *args, **kwargs)
