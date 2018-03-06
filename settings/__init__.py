

from .dynamicConfig import settings

def getValue(*args, **kwargs):
    return settings.getValue(*args, **kwargs)

def setValue(*args, **kwargs):
    settings.setValue(*args, **kwargs)

def saveToFile(*args, **kwargs):
    settings.saveToFile(*args, **kwargs)

def initialize(*args, **kwargs):
    settings.initialize(*args, **kwargs)
