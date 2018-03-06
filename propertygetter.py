

from .gconfig import *


class PropertyGetter(object):
    """descriptor class to make attribute management easier"""
    def __init__(self, key, default):
        self.key = key
        self.default = default
    def __get__(self, instance, owner):
        try:
            return instance._prop[self.key]
        except KeyError:
            if self.default is PROP_UNDEFINED:
                raise AttributeError("Property undefined: " + self.key)
            return self.default
    def __set__(self, instance, value):
        instance._prop[self.key] = value
    def __delete__(self, instance):
        del instance._prop[self.key]
        self.default = PROP_UNDEFINED
