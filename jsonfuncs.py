import json, gzip, io
from json.decoder import JSONDecodeError

from .gconfig import *

def jsondumps(obj):
    """Dump object to string."""
    serial = json.dumps(obj, sort_keys=True)
    assert(isinstance(serial, str))
    assert('\n' not in serial and '\n' not in serial)
    return serial

def jsondump(obj, filename):
    """Dump object to file."""
    from . import settings
    if settings.getValue(DYNAMIC_SETTINGS_USE_GZIP):
        with gzip.open(filename, 'wb') as file:
            json.dump(obj, file, sort_keys=True, indent=4, ensure_ascii=False)
    else:
        with io.open(filename, 'w', encoding='utf8', newline='\n') as f:
            json.dump(obj, f, sort_keys=True, indent=4, ensure_ascii=False)

def jsonloads(string):
    """Load object from string."""
    try:
        obj = json.loads(string)
    except JSONDecodeError as e:
        from . import debug
        debug.debugMessage("Failed to load json object from string")
        debug.debugMessage(string)
        raise
    return obj

def jsonload(filename):
    """Load object from file."""
    from kaiengine.resource import loadResource
    jsondat = loadResource(filename).getvalue()
    jsondat = jsondat.decode("utf8")
    jsondat = io.StringIO(jsondat)
    try:
        obj = json.load(jsondat)
    except JSONDecodeError as e:
        from . import debug
        debug.debugMessage("Failed to load json object from file: " + filename)
        debug.debugMessage(e)
        raise
    return obj
