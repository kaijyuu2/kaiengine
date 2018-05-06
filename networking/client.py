import asyncio
from kaiengine.networking.defaults import *
from kaiengine.networking.events import addClientListener, _relayEventFromServer
from kaiengine.networking.functions import _encodeObject, _decodeMessage

MESSAGE_QUEUE = []

async def _connectToServer(address, port):
    reader, writer = await asyncio.open_connection(address, port)
    await asyncio.gather(listenToServer(reader),
                         messageServer(writer))
    reader.close()
    writer.close()

def connectToServer(server_address=DEFAULT_HOST, port=DEFAULT_PORT):
    asyncio.ensure_future(_connectToServer(address, port))

async def listenToServer(reader):
    while True:
        dat = await reader.read(MAX_READ_SIZE)
        key, json_object = _decodeMessage(dat)
        _relayEventFromServer(key, json_object)

async def messageServer(writer):
    while True:
        if MESSAGE_QUEUE:
            next_message = MESSAGE_QUEUE.pop(0)
            await writer.write(next_message)
            await writer.drain()

def sendClientEvent(key, json_object):
    message = _encodeObject(key, json_object)
    MESSAGE_QUEUE.append(message)
