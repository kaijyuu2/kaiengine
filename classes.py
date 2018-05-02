
import sys
import copy
import pkgutil
import importlib
import os
from kaiengine.debug import debugMessage
from .resource import toStringPath
from .gconfig import *

classDicts = {}

def getClassDict(path):
    '''isn't necessarily loaded with all classes until one object has been properly loaded'''
    path = toStringPath(path) #turn into string
    if not path in classDicts:
        classDicts[path] = {}
    return classDicts[path]

def loadPackage(PackName):
    mod = importlib.import_module(".".join((RESOURCE_PATH, CODE_PATH, PackName)))
    return mod

def hasMainClass(member):
    try:
        if member.MainClass:
            return True
    except AttributeError:
        pass
    return False

def findClasses(classdict, packname, defaultclass):
    if not classdict:
        try:
            pack = loadPackage(packname)
        except Exception as e:
            import traceback
            traceback.print_stack()
            debugMessage(e)
            return None
        #debugMessage(pack.__dict__)
        #debugMessage(os.listdir(pack.__path__[0]))
        classdict[DEFAULT_CLASS_TYPE] = defaultclass
        for importer, modname, ispkg in pkgutil.iter_modules(pack.__path__, pack.__package__ + "."):
            mod = importlib.import_module(modname, ".")
            if mod and hasMainClass(mod):
                try:
                    classdict[mod.MainClass.type] = mod.MainClass
                except AttributeError:
                    #hackish way to get rid of the package name from __name__ but oh well
                    classdict[os.path.splitext(mod.__name__)[1][1:]] = mod.MainClass
    return classdict

#custom decorator

class directory_dict(dict):
    def __init__(self, *args, **kwargs):
        super(directory_dict, self).__init__(*args, **kwargs)
        self.directories = []



#included custom classes
def getCustGraphicObjects():
    from . import graphicobject
    directory = GRAPHIC_OBJECTS_DIR
    return findClasses(getClassDict(directory), directory, graphicobject.GraphicObject)

def getCustTilemapScenes():
    from .scene import TilemapScene
    directory = TILEMAP_SCENE_DIR
    return findClasses(getClassDict(directory), directory, TilemapScene)

def getCustActors():
    from .actor import Actor
    directory = ACTOR_DIR
    return findClasses(getClassDict(directory), directory, Actor)
