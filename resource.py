

'''Provides transparent access to loose and archived resource files.'''

import zipfile
import os
from io import BytesIO

from .gconfig import *

archive_data = {}

def setupArchive():
    global archive_handle
    from . import settings
    if settings.getValue(DYNAMIC_SETTINGS_LOAD_ARCHIVE_IN_MEMORY):
        try:
            with open(ARCHIVE_FILE_NAME, 'rb') as f:
                with zipfile.ZipFile(BytesIO(f.read()), 'r') as f:
                    archive_data.update({path: f.read(path) for path in f.namelist() })
        except IOError:
            pass


class ResourceUnavailableError(Exception):
    '''Raised when no canonical version of a resource can be found'''

def allResourcesOnPath(filepath, limitExtension=None, includeExtension=False, preferArchive=True):
    '''Returns a list of all resources (optionally, only of limitExtension) in filepath, not including subfolders.'''
    zip_compatible_path = filepath.replace("\\", "/")
    names = None
    possibleFiles = []
    if preferArchive and archive_data:
        possibleFiles = [path for path in archive_data.keys() if os.path.dirname(path) == zip_compatible_path]
    else:
        possibleFiles = os.listdir(filepath)
    if limitExtension is not None:
        possibleFiles = [path for path in possibleFiles if limitExtension in os.path.splitext(path)[1]]
    if includeExtension:
        possibleFiles = [os.path.basename(path) for path in possibleFiles]
    else:
        possibleFiles = [os.path.splitext(os.path.basename(path))[0] for path in possibleFiles]
    return possibleFiles

def checkResourceExists(filepath):
    '''Check whether resource at filepath exists, either in loose or archived form.'''
    zip_compatible_path = filepath.replace("\\", "/")
    return (zip_compatible_path in archive_data or os.path.isfile(filepath))

def loadResource(filepath):
    '''Returns the canonical handle to the resource identified by filepath, or if none exists raises ResourceUnavailableError.'''
    zip_compatible_path = filepath.replace("\\", "/")
    try:
        return BytesIO(archive_data[zip_compatible_path])
    except:
        if os.path.isfile(filepath):
            try:
                from . import debug
                debug.debugLooseMessage("LF: %s loaded from loose file" % filepath)
            except (ImportError, AttributeError): pass
            with open(filepath, "rb") as f:
                data = BytesIO(f.read())
            return data
    raise ResourceUnavailableError(filepath)


def toStringPath(path, *args):
    if path is None:
        return ""
    if len(args) > 0:
        path = [path]
        path.extend(args)
    if isinstance(path, (list, tuple)):
        return os.path.join(*path)
    return path

def toListPath(path, *args):
    if path is None:
        return []
    if len(args) > 0:
        path = [path]
        path.extend(args)
    if isinstance(path, (list, tuple)):
        return list(path)
    head, returnval = os.path.split(path)
    returnval = [returnval]
    while(len(head) > 0 and head != os.path.sep):
        head, tail = os.path.split(head)
        returnval.insert(0,tail)
    return returnval

def combineStringPaths(*args):
    return os.path.join(*args)

def getInvalidGraphicPath():
    return toStringPath(FULL_MISC_PATH + [DEFAULT_INVALID_GRAPHIC])
