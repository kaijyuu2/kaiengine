

from .gconfig import *
from .load import jsonLoad
from .resource import toStringPath, ResourceUnavailableError, allResourcesOnPath
from .settings import getValue
from .debug import debugMessage, checkDebugOn

import os, copy

localization_data = {}
localization_text = {}


UNLIKELY_DEFAULT = "_DEFAULT_ASDFASDIFNAGINAG" #something that will never be passed to getString as the default


def initLocalizationData():
    global localization_data
    try: localization_data = jsonLoad(toStringPath(FULL_STRINGS_PATH + [STRINGS_META_FILENAME]))
    except ResourceUnavailableError: pass
    for filename in allResourcesOnPath(toStringPath(FULL_STRINGS_PATH), STRINGS_EXTENSION, True):
        try:
            newdata = jsonLoad(toStringPath(FULL_STRINGS_PATH + [filename]))
        except Exception as e:
            debugMessage("Error loading localization data: " + filename)
            debugMessage(e)
            continue
        idname = os.path.splitext(filename)[0]
        for language, data in newdata.items():
            if language not in localization_text:
                localization_text[language] = {}
            localization_text[language][idname] = data

def getLocaleFont(font_key = None, locale = None):
    if locale is None: locale = getValue(DYNAMIC_SETTINGS_LOCALE)
    if font_key is None: font_key = DEFAULT_FONT
    try: return localization_data[locale][STRINGS_FONTS_KEY][font_key]
    except KeyError: return font_key

def getLocaleFontSize(font_key = None, locale = None):
    if locale is None: locale = getValue(DYNAMIC_SETTINGS_LOCALE)
    if font_key is None: font_key = DEFAULT_FONT
    return localization_data[locale][STRINGS_FONT_DEFAULT_SIZES_KEY][font_key]

def getLocaleName(locale):
    return localization_data[locale][STRINGS_LOCALE_NAME]

def getLocaleList():
    return localization_data.keys()

def getLocaleUnit(index, locale = None):
    if locale is None: locale = getValue(DYNAMIC_SETTINGS_LOCALE)
    try: 
        unitlist = localization_data[locale][STRINGS_LOCALE_UNITS]
        if len(unitlist) <= 0:
            raise KeyError #silly hack
        if index is None or index >= len(unitlist):
            index = -1
        return unitlist[index]
    except KeyError: return ""
    
def getLocaleUnitLengths(locale = None):
    if locale is None: locale = getValue(DYNAMIC_SETTINGS_LOCALE)
    try: return localization_data[locale][STRINGS_LOCALE_UNIT_LENGTHS][:]
    except KeyError: return []

def getLocaleUnitTooBig(locale = None):
    if locale is None: locale = getValue(DYNAMIC_SETTINGS_LOCALE)
    try: return localization_data[locale][STRINGS_LOCALE_UNIT_TOO_BIG]
    except KeyError: return ""

def getString(textkey, ID = None, fallbackID = None, locale = None, fallbacklocale = None, default = UNLIKELY_DEFAULT):
    locale = locale or getValue(DYNAMIC_SETTINGS_LOCALE)
    try: 
        return _getString(textkey, ID, fallbackID, locale)
    except KeyError:
        try:
            return _getString(textkey, ID, fallbackID, fallbacklocale)
        except KeyError:
            if default == UNLIKELY_DEFAULT:
                debugMessage("DEBUG: No translation in {0} or {1} for {2} using given ids of {3} or {4}".format(locale, fallbacklocale, textkey, ID, fallbackID))
                raise KeyError
            return default
        
def _getString(textkey, ID, fallbackID, locale):
    try:
        return copy.deepcopy(localization_text[locale][ID][textkey])
    except KeyError:
        return copy.deepcopy(localization_text[locale][fallbackID][textkey])
        


_ = getString #alternate name; _ used in a script to dump generated text
