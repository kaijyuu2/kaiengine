from kaiengine.networking.client import connectToServer, sendClientEvent, addClientListener
from kaiengine.networking.server import startServer, sendServerEvent, sendServerEventToAll, addServerListener

'''

WARNING: THIS MODULE IS IN AN ALPHA TESTING STATE AND HAS NOT YET BEEN
         SECURED AGAINST ATTACK. DO NOT EXPOSE A MACHINE RUNNING THIS
         CODE TO PUBLIC ACCESS.


CLIENT FUNCTIONS

    connectToServer(address, port)
        Attempt to establish a connection to a server.

    sendClientEvent(key, json_object)
        Send a JSON object to the server with the specified event key.

    addClientListener(key, listener, priority = 0)
        When a matching event is received from the server, the listener is called.
        The listener will receive:
            json_object


SERVER FUNCTIONS

    startServer(interface, port)
        Attempt to start hosting a server.

    sendServerEvent(client_id, key, json_object)
        Send a JSON object to the specified client with the specified event key.

    sendServerEventToAll(key, json_object)
        Send a JSON object to all connected clients with the specified event key.

    addServerListener(key, listener, priority = 0)
        When a matching event is received from a client, the listener is called.
        The listener will receive:
            client_id, json_object






'''
