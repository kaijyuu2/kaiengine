

#common debug functions
from .logging import logToConsole, logString
from . import settings
from .gconfig import *

def _getLogFunction():
    if checkDebugOn():
        return logToConsole
    else:
        return logString

def checkDebugOn():
    try:
        return settings.getValue(DYNAMIC_SETTINGS_DEBUG_ON)
    except KeyError:
        logToConsole("error! tried to use debug functions before settings file initiated. Assuming debug is enabled.")
        return True
    return False

def debugMessage(string):
    try:
        _getLogFunction()(string)
    except:
        _getLogFunction()("THIS TERMINAL AND/OR PYTHON INSTALL SUCKS AND CANNOT PRINT UNICODE (was trying to print a debug message and failed)")
        

def debugLooseMessage(string):
    if checkDebugOn() and settings.getValue(DYNAMIC_SETTINGS_LOOSE_WARNING, True):
        logToConsole(string)

def debugMissingMessage(string):
    if checkDebugOn() and settings.getValue(DYNAMIC_SETTINGS_MISSING_FILE_WARNING, True):
        logToConsole(string)

def debugHasKeyMessage(propDict, key, name = None):
    if checkDebugOn() and settings.getValue(DYNAMIC_SETTINGS_PRINT_UNKNOWN_KEYS, True) and propDict is not None:
        try:
            has_key = key in propDict
        except (AttributeError, TypeError): #maybe it's an object
            has_key = hasattr(propDict, key)
        if not has_key:
            if not settings.getValue(DYNAMIC_SETTINGS_SKIP_UNDERSCORE_KEYS, True) or key[0] != "_":
                string = "Unknown key: \"" + key + "\"."
                if name is not None:
                    string += " File or Class name: " + name
                logToConsole(string)
