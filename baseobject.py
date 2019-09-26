

"""game object type that includes stuff for loading/etc"""

from .propertygetter import PropertyGetter
from .destroyinterface import DestroyInterface
from . import load
import copy
from .gconfig import *


SPECIAL_KEYS = [PATH, EXTENSION, CLASS_TYPE, FILENAME, FILE_EXTENSION,
            FILEPATH, FAILED_LOAD_KEY, ADDED_CLASS_TYPE] #don't put these in the serialized dictionary


class BaseObject(DestroyInterface):

    #default attributes. Should really be set by the child classes
    vars()[PATH] = [] #for any dynamic child classes
    vars()[EXTENSION] = None #file extension for dynamic child classes

    def __init__(self, filepath = None, *args, **kwargs):
        super(BaseObject, self).__init__(*args, **kwargs)
        self._prop = {}
        self.loadProp(filepath)

    def loadProp(self, filepath):
        from .resource import ResourceUnavailableError
        file_failed_to_load = False
        if filepath is not None:
            try: #check if already loaded
                filepath.keys() #is if this is a dict
            except AttributeError:
                if not (type(filepath) is list or type(filepath) is tuple): #check if it's just the filename or a full path
                    filepath = self._path + [filepath] #make it a full path if not one already
                try:
                    new_properties = load.loadGenericObj(filepath, self._extension)
                except ResourceUnavailableError:
                    new_properties = {}
                    file_failed_to_load = True
            else:
                new_properties = filepath
        else:
            new_properties = {}
        self.setupProperties(new_properties)
        if file_failed_to_load:
            raise ResourceUnavailableError("Properties file not found: " + str(filepath))

    def setupProperties(self, new_properties):
        #for when the object is first loaded
        extra_prop = {}
        for classtype in reversed(type(self).mro()):
            try:
                extra_prop.update(classtype.default_prop)
            except AttributeError:
                pass
        extra_prop = copy.deepcopy(extra_prop) #copy any nested dicts/lists/etc
        for key, val in extra_prop.items():
            self.addProperty(key, val)
        self.applyProperties(new_properties, extra_prop)

    def applyProperties(self, new_properties, extra_prop = None):
        #if you want to apply a new dict of properties later (also used in loading)
        for key, val in new_properties.items():
            try:
                from . import debug
                debug.debugHasKeyMessage(extra_prop, key, self.getFilename(new_properties))
            except (ImportError, AttributeError):
                pass
            self.addProperty(key, val)

    def addProperty(self, key, value):
        default = getattr(self, key, PROP_UNDEFINED)
        setattr(type(self), key, PropertyGetter(key, default))
        self._prop[key] = value

    def getProperty(self, key, default = DEFAULT_KWARG):
        try: return self._prop[key]
        except KeyError:
            if default == DEFAULT_KWARG:
                raise
            return default

    def getFilename(self, prop = None):
        if prop is None:
            try:
                prop = self._prop
            except AttributeError:
                prop = {}
        try:
            return prop[FILENAME]
        except KeyError:
            return type(self).__name__

    def getFilepath(self, prop = None):
        if prop is None:
            try:
                prop = self._prop
            except AttributeError:
                prop = {}
        try:
            return prop[FILEPATH]
        except KeyError:
            return []

    def getFileExtension(self, prop = None):
        if prop is None:
            try:
                prop = self._prop
            except AttributeError:
                prop = {}
        try:
            return prop[FILE_EXTENSION]
        except KeyError:
            return ""


    def getFullFilepath(self, prop = None):
        return self.getFilepath(prop) + [self.getFilename(prop) + self.getFileExtension(prop)]

    def serialize(self):
        new_prop = copy.deepcopy(self._prop)
        for key in SPECIAL_KEYS:
            new_prop.pop(key, None)
        return new_prop
