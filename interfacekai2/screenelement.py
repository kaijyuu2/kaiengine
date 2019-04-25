# -*- coding: utf-8 -*-

#most basic element
import copy

from kaiengine.event import customEvent
from kaiengine.event import MOUSE_PARTITION_SIZE_X, MOUSE_PARTITION_SIZE_Y, EVENT_MOUSE_MOVE_SECTION
from kaiengine.objectinterface import GraphicInterface, EventInterface, SchedulerInterface

from .basiceventkeys import *

class ScreenElement(GraphicInterface, EventInterface, SchedulerInterface):
    
    _event_keys = copy.copy(BASIC_EVENT_KEYS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = {}
        self._funcs = {}
        self._hidden = set()
        self.focus = False
        for string in self._event_keys:
            try:
                self._funcs[string] = getattr(self, string)
            except AttributeError:
                pass
            try:
                self._funcs[string] = kwargs[string]
            except KeyError:
                pass
        
    @property
    def position(self):
        '''alias for pos attribute'''
        return self.pos

    @property
    def dimensions(self):
        return (self.width, self.height)

    @property
    def width(self):
        return self.getWidth()
    @width.setter
    def width(self, newval):
        self.setWidth(newval)

    @property
    def height(self):
        return self.getHeight()
    @height.setter
    def height(self, newval):
        self.setHeight(newval)

    @property
    def children(self):
        return self.getAllChildren()

    @property
    def extents(self):
        return self.getExtents()

    @property
    def mouse_move_partitions(self):
        return _getRelevantMousePartitions(*self.extents)
    
    def callEventFunc(self, key, *args, **kwargs):
        if key in self._funcs:
            self._funcs[key](*args, **kwargs)
    
    def getEventKey(self, key = ""):
        return str(self.id) + "_" + key + "_EVENT"
    
    def getEventCaller(self, key, *args, **kwargs):
        #convenience function for delaying a custom event
        return lambda: customEvent(key, *args, **kwargs)
    
    def _gainFocus(self):
        if not self.focus:
            self.focus = True
            self.addFocusListeners()
            self.callEventFunc(GAIN_FOCUS_KEY)
            
    def _loseFocus(self):
        if self.focus:
            self.focus = False
            self.removeFocusListeners()
            self.callEventFunc(LOSE_FOCUS_KEY)
            
    def addFocusListeners(self):
        self.addListener()

    def checkPointWithinElement(self, x, y):
        extents = self.extents
        return extents[0] <= x <= extents[2] and extents[1] <= y <= extents[3]

    def getWidth(self):
        return self.getSpriteWidth()
    
    def setWidth(self, newval):
        self.setSpriteWidth(newval)
    
    def getHeight(self):
        return self.getSpriteHeight()
    
    def setHeight(self, newval):
        self.setSpriteHeight(newval)
        
    def getExtents(self):
        return self.getSpriteExtentsMinusCamera()

    def _childPosition(self, child_id):
        return self.getPos()

    def setPosition(self, *args, **kwargs):
        '''alias for setPos'''
        self.setPos(*args, **kwargs)

    def setPos(self, *args, **kwargs):
        super().setPos(*args, **kwargs)
        self._applyPosition()
        for child in self.children:
            child.setPos(self._childPosition(child.id))

    def shiftPosition(self, *args, **kwargs):
        '''alias for movePos'''
        self.movePos(*args, **kwargs)

    def movePos(self, *args, **kwargs):
        super().movePos(*args, **kwargs)
        self._applyPosition()
        for child in self.children:
            child.movePos(*args, **kwargs)

    def _applyPosition(self):
        pass

    def addChild(self, newchild):
        self._children[newchild.id] = newchild
        return newchild
    
    def getChild(self, child_id):
        return self._children[child_id]
    
    def getAllChildren(self):
        return self._children.values()
    
    def hide(self, key = None):
        if key is None:
            key = self.id
        self._hidden.add(key)
        for child in self.getAllChildren():
            child.hide(key)
        self.setSpriteShow(False)
        
    def unhide(self, key = None):
        if key is None:
            key = self.id
        self._hidden.remove(key)
        for child in self.getAllChildren():
            child.unhide(key)
        if not self.isHidden():
            self.setSpriteShow(True)
            
    def isHidden(self):
        return bool(self._hidden)
        
    
    
def _getRelevantMousePartitions(x_min, y_min, x_max, y_max):
    x_values = [x for x in range(x_min//MOUSE_PARTITION_SIZE_X, (x_max//MOUSE_PARTITION_SIZE_X)+1)]
    y_values = [y for y in range(y_min//MOUSE_PARTITION_SIZE_Y, (y_max//MOUSE_PARTITION_SIZE_Y)+1)]
    relevant_keys = [EVENT_MOUSE_MOVE_SECTION[(x, y)] for x in x_values for y in y_values]
    return relevant_keys

