

import os
from json.decoder import JSONDecodeError

from . import load
from . import jsonfuncs
from . import settings
import copy
from .resource import ResourceUnavailableError, toStringPath

from .gconfig import *

_DEFAULT_VAL_ = "_DEFAULT_VALUE_ hey what are you doing reading my code you hooligan"
_TEST_FILENAME = "_test_.___"

savedata = {}
currentsave = None

def Initialize(filepath = None):
    if filepath is None:
        filepath = settings.getValue(DYNAMIC_SETTINGS_SAVE_PATH, None)
    if filepath is not None:
        filepath = toStringPath(filepath)
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
    resetToDefaultSave()

def resetToDefaultSave():
    from .debug import debugMessage
    global currentsave
    try:
        _loadSave(settings.getValue(DYNAMIC_SETTINGS_DEFAULT_SAVE_FILENAME), settings.getValue(DYNAMIC_SETTINGS_DEFAULT_SAVE_PATH))
        currentsave = None
    except JSONDecodeError as e:
        debugMessage(e)
    except ResourceUnavailableError:
        debugMessage("Failed to load default save. Ignore this if the game isn't supposed to have one.")
    except:
        raise

def setValue(key, value):
    savedata[key] = value

def saveDictionaryValues(dictionary):
    savedata.update(dictionary)

def getValue(key, default_val = _DEFAULT_VAL_):
    try: return savedata[key]
    except KeyError:
        if default_val != _DEFAULT_VAL_:
            return default_val
        raise #raise the original key error

def removeValue(key):
    try: del savedata[key]
    except KeyError: pass

def getEntireSaveDictionary(): #warning: slow
    return copy.deepcopy(savedata)

def loadSave(filename): #dumps all current save data! save first if needed
    global currentsave
    try:
        _loadSave(filename)
        currentsave = filename
    except ResourceUnavailableError:
        from .debug import debugMessage
        debugMessage("Failed to load save: " + filename)

def _loadSave(filename, filepath = None):
    global savedata
    savedata = getSaveData(filename, filepath)

def getSaveData(filename, filepath = None):
    filename = os.path.splitext(filename)[0] + SAVE_EXTENSION
    if filepath is None:
        filepath = settings.getValue(DYNAMIC_SETTINGS_SAVE_PATH)
    newpath = toStringPath(filepath + [filename])
    return load.jsonLoad(newpath)

def commitSave(filename = None):
    global currentsave
    if filename == None:
        filename = currentsave
    if filename != None:
        filename = os.path.splitext(filename)[0] + SAVE_EXTENSION
        path = toStringPath(settings.getValue(DYNAMIC_SETTINGS_SAVE_PATH) + [filename])
        try: #test to make sure it works correctly
            savestring = jsonfuncs.jsondumps(savedata)
            jsonfuncs.jsonloads(savestring)
        except:
            from .debug import debugMessage
            debugMessage("Failed to dump savegame. Aborting!")
            raise
            return False
        try:
            jsonfuncs.jsondump(savedata, path)
        except PermissionError:
            from .debug import debugMessage
            debugMessage("Failed to save game due to not having write permissions. Aborting!")
            return False
        currentsave = filename
        return True
    else:
        from .debug import debugMessage
        debugMessage("Failed to save game; no filename passed and either no save loaded or only default save loaded.")
    return False

def getCurrentSaveFilename(): #returns None if using default save
    return currentsave

def getAllSaveFiles(filepath = None):
    if filepath is None:
        filepath = settings.getValue(DYNAMIC_SETTINGS_SAVE_PATH)
    filepath = toStringPath(filepath)
    return [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f)) and os.path.splitext(f)[1] == SAVE_EXTENSION]

def testSaveWorking():
    try:
        path = toStringPath(settings.getValue(DYNAMIC_SETTINGS_SAVE_PATH) + [_TEST_FILENAME])
        jsonfuncs.jsondump(jsonfuncs.jsondumps({}), path)
        jsonfuncs.jsonload(path)
        os.remove(path)
    except Exception as e:
        from .debug import debugMessage
        debugMessage("Save game test failed.")
        debugMessage(e)
        return False
    return True

