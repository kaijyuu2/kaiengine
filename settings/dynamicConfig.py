

import os

from kaiengine import savegame
from kaiengine.baseobject import BaseObject
from kaiengine.jsonfuncs import jsondump, jsondumps
from kaiengine.resource import ResourceUnavailableError, checkResourceExists, toStringPath

from kaiengine.gconfig import *

_DEFAULT_VALUE_ = "_DEFAULT_VALUE_dfhzdfhzegag" #something that will never be passed

class Settings(BaseObject):

    vars()[PATH] = [] #main directory
    vars()[EXTENSION] = CONFIG_EXTENSION


    def __init__(self, filepath):
        self._initialized = False
        newfilepath = filepath
        if CONFIG_EXTENSION not in filepath:
            newfilepath += CONFIG_EXTENSION
        if checkResourceExists(toStringPath(self._path + [newfilepath])):
            try:
                super(Settings, self).__init__(newfilepath)
            except:
                self.altInit(filepath)
        else:
            self.altInit(filepath)
        self._altered_values = self.serialize()

    def altInit(self, filepath):
        super(Settings, self).__init__()
        self._prop[FILEPATH] = []
        self._prop[FILE_EXTENSION] = CONFIG_EXTENSION
        self._prop[FILENAME] = filepath

    def initialize(self, game_default_settings = {}):
        for key, val in list(game_default_settings.items()):
            if key not in self._prop:
                self._prop[key] = val
                setattr(self, key, val)
        for key, val in list(DEFAULT_DYNAMIC_SETTINGS.items()):
            if key not in self._prop:
                self._prop[key] = val
                setattr(self, key, val)
        self._initialized = True

    def saveToFile(self):
        try:
            serialized = self._altered_values
            jsondumps(serialized)
        except Exception as e:
            from kaiengine.debug import debugMessage
            debugMessage("Settings serialization error:")
            debugMessage(e)
        else:
            try:
                jsondump(serialized, toStringPath(self.getFullFilepath()))
            except Exception as e:
                from kaiengine.debug import debugMessage
                debugMessage("Settings file save error:")
                debugMessage(e)

    def getValue(self, key, default_val = _DEFAULT_VALUE_):
        try: #preferentially try to get it from the save; use globals if it doesn't exist
            savegame.getValue(key)
        except KeyError:
            try:
                return getattr(self, key)
            except AttributeError:
                if default_val != _DEFAULT_VALUE_:
                    return default_val
                raise KeyError("No settings value found for: \"" + key + "\"" + (" Probable cause: Dynamic Settings not initalized yet! Be sure to call initialize on the settings driver before trying to use it." if not self._initialized else ""))

    def setValue(self, key, value = True):
        self._prop[key] = value
        self._altered_values[key] = value
        setattr(self, key, value)

settings = Settings(SETTINGS_FILE_NAME)
