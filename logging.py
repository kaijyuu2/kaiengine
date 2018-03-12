# -*- coding: utf-8 -*-

import os, time, logging
from kaiengine.gconfig.paths import LOG_EXTENSION, LOG_PATH, LOG_FILENAME_HEADER
from kaiengine.resource import toStringPath


DATE_TIME = time.strftime("%d_%m_%Y") + "__" + time.strftime("%H_%M_%S")

DEFAULT_FILEPATH = "logfile___" + DATE_TIME + LOG_EXTENSION

REGULAR_SPACER = "---------------------------"
REGULAR_INFO = "Kai Engine logfile."
REGULAR_INFO_2 = "Date and time: " + DATE_TIME

logger_init_completed = False

def initLogger(*args, **kwargs):
    if not os.path.isdir(LOG_PATH):
        os.makedirs(LOG_PATH)
    _initLogger(toStringPath(*[LOG_PATH, LOG_FILENAME_HEADER + LOG_EXTENSION]))

def _initLogger(filepath = None, extra_text = None):
    global logger_init_completed
    if not filepath: filepath = DEFAULT_FILEPATH
    try: 
        logging.basicConfig(filename = filepath, level = logging.INFO)
        logger_init_completed = True
        logStringInfo(REGULAR_SPACER)
        logStringInfo(REGULAR_INFO)
        logStringInfo(REGULAR_INFO_2)
        if extra_text:
            logStringInfo(extra_text)
    except PermissionError:
        print("Logger couldn't start; write permissions denied")
        
def logStringWarning(string):
    if logger_init_completed:
        logging.warning(string)
    
def logStringDebug(string):
    logString(string)
        
def logString(string):
    logStringWarning(string)

def logStringInfo(string):
    if logger_init_completed:
        logging.info(string)

def logToConsole(string):
    logString(string)
    print(string)
    
def getLogDateTimeString():
    return DATE_TIME
    