from kaiengine.event import customEvent, addCustomListener
from kaiengine.networking.defaults import *

def _relayEventFromClient(key, client_id, json_object):
    customEvent(_CLIENT_EVENT_PREFIX+key, client_id, json_object)

def _relayEventFromServer(key, json_object):
    customEvent(_SERVER_EVENT_PREFIX+key, json_object)

def addClientListener(key, listener, priority = 0):
    addCustomListener(_SERVER_EVENT_PREFIX+key, listener, priority=priority)

def addServerListener(key, listener, priority = 0):
    addCustomListener(_CLIENT_EVENT_PREFIX+key, listener, priority=priority)
