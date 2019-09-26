# -*- coding: utf-8 -*-

import os, copy, importlib

from kaiengine.propertygetter import PropertyGetter
from kaiengine.resource import toStringPath, toListPath
from kaiengine.load import loadGenericObj
from kaiengine.destroyinterface import DestroyInterface

from kaiengine.gconfig import PATH, EXTENSION, FILENAME, FILE_EXTENSION, FILEPATH, FAILED_LOAD_KEY, ADDED_CLASS_TYPE
from kaiengine.gconfig import CLASS_TYPE, DEFAULT_CLASS_TYPE, PYTHON_EXTENSION, PROP_UNDEFINED, DEFAULT_KWARG

SPECIAL_KEYS = [PATH, EXTENSION, CLASS_TYPE, FILENAME, FILE_EXTENSION,
            FILEPATH, FAILED_LOAD_KEY, ADDED_CLASS_TYPE] #don't put these in the serialized dictionary

_class_types_dict = {}


class KaiObject(DestroyInterface):

    #default attributes. Should really be set by the child classes
    vars()[PATH] = [] #for any dynamic child classes
    vars()[EXTENSION] = None #file extension for dynamic child classes

    def __init__(self, *args, properties_dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._prop = {}
        if properties_dict:
            self.loadProp(properties_dict)

    def loadProp(self, properties_dict):
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
        self.applyProperties(properties_dict, extra_prop)

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

def createObject(filepath, *args, default_type = KaiObject, **kwargs):
    filepath = toStringPath(filepath)
    prop = loadGenericObj(filepath)
    try:
        class_name = prop.pop(CLASS_TYPE)
        if class_name != DEFAULT_CLASS_TYPE:
            class_path = os.path.join(os.path.dirname(filepath), class_name + PYTHON_EXTENSION)
            try:
                class_type = _class_types_dict[class_path]
            except KeyError:
                if prop.get(ADDED_CLASS_TYPE, False) and not os.path.isfile(class_path): #check if auto generated class type doesn't exist
                    raise KeyError #hack to avoid duplicated code
                spec = importlib.util.spec_from_file_location(".".join(toListPath(os.path.splitext(class_path)[0])), class_path)
                newmod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(newmod)
                class_type = newmod.MainClass
                _class_types_dict[class_path] = class_type
        else:
            raise KeyError #hack to avoid duplicated code
    except KeyError:
        class_type = default_type
    return class_type(*args, properties_dict = prop, **kwargs)

def createObjectWithData(obj_filename, obj_filedir, obj_ext, default_type, *args, **kwargs): #for making wrappers
    path = toStringPath(toListPath(obj_filedir) + toListPath(obj_filename))
    if obj_ext not in path:
        path += obj_ext
    if default_type is not None:
        kwargs["default_type"] = default_type
    return createObject(path, *args, **kwargs)

'''
example wrapper function

def createMap(filename, *args, **kwargs):
    return createObjectWithData(filename, MAPS_PATH, MAP_EXTENSION, MapObject, *args, **kwargs)

serves similar purpose to old BaseObject construction functions, if full filepaths and/or default types want to be inferred
createObject alone is sufficient if full paths and default class types are provided
'''
