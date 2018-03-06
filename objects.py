

from . import load
from . import classes
import traceback

from kaiengine.debug import debugMessage
from kaiengine.resource import ResourceUnavailableError

from .gconfig import *

def createObjectFin(classdict, class_type, prop, *args, **kwargs):
    #prop can be 1) a filename, 2) a full filepath, 3) a loaded data dict, 4) None (default settings)
    if class_type is None:
        class_type = DEFAULT_CLASS_TYPE
    if class_type in classdict:
        return classdict[class_type](prop, *args, **kwargs)
    else:
        if class_type == DEFAULT_CLASS_TYPE:
            raise ResourceUnavailableError("Failed to load default object class type. Something busted, yo.")
        if not FAILED_LOAD_KEY in prop:
            if CLASS_TYPE in prop and ADDED_CLASS_TYPE not in prop:
                raise ResourceUnavailableError("Failed to load object. Invalid class type, possibly? (check _TYPE) " + class_type)
            else:
                #debugMessage(classdict)
                return createObjectFin(classdict, None, prop, *args, **kwargs)
        else:
            raise ResourceUnavailableError("Failed to load object. Make sure prop file and/or .py file exists. " + class_type)

def createObject(filepath, full_path, extension, cust_method, *args, **kwargs):
    if isinstance(filepath, str): #todo: update for python 3 syntax too
        filepath = full_path + [filepath]
    prop = load.loadGenericObj(filepath, extension)
    class_type = prop[CLASS_TYPE]
    prop.pop(CLASS_TYPE)
    if filepath is not None:
        filepath = filepath[-2] #rip directory out of it
    return createObjectFin(cust_method(filepath), class_type, prop, *args, **kwargs)


def createGraphicObject(class_type = None, prop = None, *args, **kwargs):
    return createObjectFin(classes.getCustGraphicObjects(), class_type, prop, *args, **kwargs)
