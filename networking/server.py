import asyncio
from kaiengine.networking.defaults import *
from kaiengine.networking.events import addServerListener, _relayEventFromClient
from kaiengine.networking.functions import _encodeObject, _decodeMessage
from kaiengine.uidgen import generateUniqueID

SERVER_MESSAGE_QUEUE = {}

def sendServerEventToAll(key, json_object):
    message = _encodeObject(key, json_object)
    for client_id in SERVER_MESSAGE_QUEUE:
        SERVER_MESSAGE_QUEUE[client_id].append(message)

def sendServerEvent(client_id, key, json_object):
    message = _encodeObject(key, json_object)
    SERVER_MESSAGE_QUEUE[client_id].append(message)

async def _listenToClient(client_id, reader):
    while True:
        dat = await reader.read(MAX_READ_SIZE)
        key, json_object = _decodeMessage(dat)
        _relayEventFromClient(client_id, key, json_object)

async def _messageClient(client_id, writer):
    while True:
        if SERVER_MESSAGE_QUEUE[client_id]:
            next_message = SERVER_MESSAGE_QUEUE[client_id].pop(0)
            await writer.write(next_message)
            await writer.drain()

async def _handleNewClient(reader, writer):
    client_id = generateUniqueID("_NETWORK_CLIENT_")
    SERVER_MESSAGE_QUEUE[client_id] = []
    await asyncio.gather(_listenToClient(client_id, reader),
                         _messageClient(client_id, writer))
    reader.close()
    writer.close()

async def _startServer(interface, port):
    server = await asyncio.start_server(_handleNewClient, interface, port)
    #loop until done..?
    #server.close()

def startServer(interface=DEFAULT_INTERFACE, port=DEFAULT_PORT):
    asyncio.ensure_future(_startServer(port))
