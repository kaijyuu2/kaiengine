import asyncio
from kaiengine.networking.defaults import *
from kaiengine.networking.events import addServerListener, _relayEventFromClient

SERVER_MESSAGE_QUEUES = {}

def sendServerEventToAll(key, json_object):
    message = _encodeObject(key, json_object)
    for message_queue in SERVER_MESSAGE_QUEUES.values():
        message_queue.append(message)

def sendServerEvent(client_id, key, json_object):
    message = _encodeObject(key, json_object)
    SERVER_MESSAGE_QUEUES[client_id].append(message)

def _startServer(port):
    #NYI
    pass

def startServer(port=DEFAULT_PORT):
    asyncio.ensure_future(_startServer(port))
