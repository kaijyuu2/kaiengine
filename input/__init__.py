import .pygletkeys

KEYS = pygletkeys.KEYS

def standardizedKey(raw_key):
    try:
        return KEYS[raw_key]
    except KeyError:
        return str(raw_key)
