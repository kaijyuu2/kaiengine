from kaiengine.jsonfuncs import jsondumps, jsonloads
from kaiengine.networking.defaults import *

def _encodeObject(key, json_object):
    json_string = jsondumps(json_object)
    message = 'MSG_JSON\n{{"key":{0},"data":{1}}}'.format(key, json_string)
    message = msg.encode("utf8")
    return message

def _decodeMessage(message_string):
    message = message_string.decode("utf8")
    if len(message) >= 10:
        if message[0:8] == "MSG_JSON":
            wrapper = jsonloads(message[9:])
            return wrapper["key"], wrapper["data"]
