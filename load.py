

#for filepaths and such
from kaiengine.gconfig import *
try:
    from . import jsonfuncs
    from . import fonts
except ImportError:
    from . import jsonfuncs
    from . import fonts
import os
import copy
import zipfile
from kaiengine.debug import debugMessage
from kaiengine.resource import checkResourceExists, ResourceUnavailableError, toStringPath, toListPath
from .updatenesteddict import updateNestedDict
from .classes import getClassDict

LoadedData = {}
LoadedAnis = {}

def loadText(filename):
    with open(toStringPath(RESOURCE_PATH, TEXT_DIR, filename), "r") as myfile:
        data=myfile.read()
    return data

class LoadDict(dict):
    def update(self, newdict):
        super(LoadDict, self).update(newdict)
        return self

def resource_path( filepath):
    return toStringPath(RESOURCE_PATH, filepath)

def jsonLoad(path):
    data = jsonfuncs.jsonload(toStringPath(path))
    try: del data[META_KEY]
    except KeyError: pass
    return data

def load_graphic_font_data(filepath):
    filepath = fonts.getFontPath(filepath)
    if GRAPHIC_FONT_EXTENSION not in filepath:
        filepath += GRAPHIC_FONT_EXTENSION
    obj = load_object_no_class(filepath)
    if PROP_KEY in obj:
        newpath = toStringPath(os.path.split(filepath)[0] , obj[PROP_KEY])
        obj = updateNestedDict(load_graphic_font_data(newpath), obj)
        obj.pop(PROP_KEY)
    return obj

def loadGraphicFont2Data(filepath):
    filepath = fonts.getFontPath(filepath)
    if GRAPHIC_FONT_2_EXTENSION not in filepath:
        filepath += GRAPHIC_FONT_2_EXTENSION
    obj = load_object_no_class(filepath)
    if PROP_KEY in obj:
        newpath = toStringPath(os.path.split(filepath)[0] , obj[PROP_KEY])
        obj = updateNestedDict(loadGraphicFont2Data(newpath), obj)
        obj.pop(PROP_KEY)
    return obj

def loadGraphicFont3Data(filepath):
    filepath = fonts.getFontPath(filepath)
    if GRAPHIC_FONT_3_EXTENSION not in filepath:
        filepath += GRAPHIC_FONT_3_EXTENSION
    obj = load_object_no_class(filepath)
    if PROP_KEY in obj:
        newpath = toStringPath(os.path.split(filepath)[0] , obj[PROP_KEY])
        obj = updateNestedDict(loadGraphicFont3Data(newpath), obj)
        obj.pop(PROP_KEY)
    return obj

def load_graphic_font_glyph_paths(filepath):
    from kaiengine.debug import debugLooseMessage
    filepath = fonts.getFontPath(filepath)
    paths = set()
    try:
        try:
            with zipfile.ZipFile(ARCHIVE_FILE_NAME) as f:
                names = f.namelist()
        except:
            debugLooseMessage("Could not load gfont name list from %s" % ARCHIVE_FILE_NAME)
        altered_path = filepath.replace("\\", "/")
        tempPaths = [path for path in names if altered_path in path]
        paths.update([path for path in tempPaths if IMAGE_EXTENSION in path])
    except:
        debugLooseMessage("Could not load gfonts from %s" % ARCHIVE_FILE_NAME)
    try:
        paths.update([toStringPath(filepath, obj) for obj in os.listdir(filepath) if IMAGE_EXTENSION in obj])
    except:
        debugLooseMessage("Could not load loose gfonts.")
    return list(paths)

def load_font_paths():
    from kaiengine.debug import debugLooseMessage
    filepath = fonts.getFontPath()
    paths = set()
    try:
        try:
            with zipfile.ZipFile(ARCHIVE_FILE_NAME) as f:
                names = f.namelist()
        except:
            debugLooseMessage("Could not load font name list from resources.dat.")
        paths.update([path for path in names if os.path.splitext(path)[1] in SUPPORTED_FONTS])
    except Exception as e:
        debugLooseMessage("Could not load fonts from resources.dat.")
    try:
        paths.update([toStringPath(filepath, obj) for obj in os.listdir(filepath) if os.path.splitext(obj)[1] in SUPPORTED_FONTS])
    except:
        debugLooseMessage("Could not load loose fonts.")
    return list(paths)

def load_animation( filepath): #adds the sprite and resource path directories
    return load_ani(os.path.join(RESOURCE_PATH,filepath))

def load_ani(filepath): #assumes the path has already been created:
    if filepath not in list(LoadedAnis.keys()):
        path = os.path.splitext(filepath)
        if path[1] != ANI_EXTENSION:
            filepath = os.path.join(path[0] + ANI_EXTENSION)
        try:
            newani = jsonLoad(filepath)
            if PROP_KEY in list(newani.keys()):
                newani = updateNestedDict(load_ani(os.path.join(os.path.dirname(filepath), newani[PROP_KEY])), newani)
                del newani[PROP_KEY]
            LoadedAnis[filepath] = newani
        except ResourceUnavailableError:
            LoadedAnis[filepath] = {}
    return copy.deepcopy(LoadedAnis[filepath])



def load_object_no_class(path, raise_error = True):
    #loads an object; doesn't set class type if it doesn't exist. Returns FAILED_LOAD_KEY in dict upon failure with raise_error set to true
    try: obj = LoadDict(jsonLoad(path))
    except ResourceUnavailableError:
        if raise_error:
            raise ResourceUnavailableError("Could not load prop file. " + path)
        obj = LoadDict({FAILED_LOAD_KEY: True})
    temp_filepath, temp_filename = os.path.split(path)
    filepath = toListPath(temp_filepath)
    filename, fileext = os.path.splitext(temp_filename)
    obj[FILENAME] = filename
    obj[FILEPATH] = filepath
    obj[FILE_EXTENSION] = fileext
    return obj

def load_object(path):
    #loads an object and adds the class type if appropriate
    obj = load_object_no_class(path, False)
    obj = _load_object_add_class(obj, path)
    return obj

def _load_object_add_class(obj, path):
    if CLASS_TYPE not in obj:
        obj[CLASS_TYPE] = os.path.splitext(os.path.basename(path))[0]
        obj[ADDED_CLASS_TYPE] = True
    return obj

def load_game_object(filepath, extension, path):
    #included for backwards compatibility. Use loadGenericObj
    return loadGenericObj(path + [filepath], extension)

def loadGenericObj(filepath, extension = None):
    #includes fixing file extension and doing inheritence
    if filepath is None:
        return {FILE_EXTENSION: extension,
            CLASS_TYPE: DEFAULT_CLASS_TYPE}
    filepathstr = toStringPath(filepath) #turn into string
    filepathlist = toListPath(filepath) #make sure we have a list too
    if extension is not None and extension not in filepathstr:
        filepathstr += extension
    if filepathstr not in LoadedData:
        obj = load_object_no_class(filepathstr, False)
        if PROP_KEY in list(obj.keys()):
            if obj[PROP_KEY] == filepathlist[-1]:
                debugMessage("infinitely recursive prop detected! Did you use prop instead of type?")
                debugMessage(filepathstr)
            else:
                obj = updateNestedDict(loadGenericObj(filepathlist[:-1] + [obj[PROP_KEY]], extension), obj)
            obj.pop(PROP_KEY)
        obj = _load_object_add_class(obj, filepathstr)
        LoadedData[filepathstr] = copy.deepcopy(obj)
    else:
        obj = copy.deepcopy(LoadedData[filepathstr])
    return obj

def load_graphicobject(filepath):
    return load_game_object(filepath, GRAPHIC_OBJECT_EXTENSION, FULL_GRAPHIC_OBJECTS_PATH)






