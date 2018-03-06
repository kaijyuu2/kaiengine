

# multi layer bool that uses keys

# call set() with a key and a boolean value
# call check() to see whether any keys have been set to True
# check() returns False if no keys have been set, True otherwise

DEFAULT_KEY_BOOL_KEY = "_default_key_bool"

class KeyBool(object):
    def __init__(self):
        self._keys = set()

    def set(self, key = None, val = True):
        if key is None: key = DEFAULT_KEY_BOOL_KEY
        if val:
            self._keys.add(key)
        else:
            try: self._keys.remove(key)
            except KeyError: pass


    def check(self):
        return self._keys

    def reset(self):
        self._keys = set()
