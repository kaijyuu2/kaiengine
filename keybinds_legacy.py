
from pyglet.window.key import symbol_string

import copy

bound_keys = {}

def keyMatches(bindName, key):
    try:
        return key in bound_keys[bindName]
    except KeyError:
        raise NotImplementedError("Keybind {0} does not exist in keybind lookup table: {1}".format(bindName, bound_keys))
    return False

def keyMatchesAny(bindNames, key):
    for bind in bindNames:
        if keyMatches(bind, key):
            return True
    return False

def keyNameBound(bindName):
    return bindName in bound_keys

def keyBound(key):
    for bind in list(bound_keys.keys()):
        if keyMatches(bind, key):
            return True
    return False

def keyName(key):
    #TODO: reverse dict to facilitate efficiency of this (rest should be used less now)
    for bind in bound_keys.keys():
        if keyMatches(bind, key):
            return bind
    return None #key not bound

def getBindNameString(bindName):
    try:
        return getKeyNameString(bound_keys[bindName][0])
    except (KeyError, IndexError):
        return "INVALID KEY"

def getKeyNameString(key):
    try: return symbol_string(key)
    except TypeError: return str(key)

def addBoundKey(bindName, key, index = None):
    if bindName in bound_keys:
        if index is None:
            if key not in bound_keys[bindName]:
                bound_keys[bindName].append(key)
        else:
            bound_keys[bindName].extend([None]*(index - len(bound_keys[bindName]) + 1)) #pad list if necessary
            bound_keys[bindName][index] = key
    else:
        bound_keys[bindName] = [key]

def addBoundKeyDict(bindDict):
    for key, val in list(bindDict.items()):
        for keybind in val:
            addBoundKey(key, keybind)

def clearBoundKeys():
    bound_keys.clear()

def removeBoundKey(bindName, key):
    if bindName in bound_keys:
        try:
            bound_keys[bindName].pop(bound_keys[bindName].index(key))
            if len(bound_keys[bindName]) < 1:
                del bound_keys[bindName]
        except ValueError:
            pass

def getBoundKeys():
    return copy.deepcopy(bound_keys)

def checkKeyBound(keyname, remove=False):
    for key, keylist in list(bound_keys.items()):
        index = -1
        for i, boundkeyname in enumerate(keylist):
            if boundkeyname == keyname:
                index = i
                break
        if index >= 0:
            if remove:
                bound_keys[key][index] = None
            return key, index
    return False

def changeBoundKey(bindName, key):
    removeBoundKey(bindName, key)
    addBoundKey(bindName, key)
