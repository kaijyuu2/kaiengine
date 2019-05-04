# -*- coding: utf-8 -*-

#most basic element
import copy
import operator

from kaiengine.event import customEvent
from kaiengine.event import MOUSE_PARTITION_SIZE_X, MOUSE_PARTITION_SIZE_Y, EVENT_MOUSE_MOVE_SECTION
from kaiengine.objectinterface import GraphicInterface, EventInterface, SchedulerInterface
from kaiengine.weakrefhelper import weakRef, unWeakRef
from kaiengine.debug import debugMessage
from kaiengine.gconfig.default_keybinds import *

from .basiceventkeys import *

DEFAULT_INPUT_LOCK = "_DEFAULT_INPUT_LOCK"

class ScreenElement(GraphicInterface, EventInterface, SchedulerInterface):
    
    _focus_event_keys = copy.copy(FOCUS_EVENT_KEYS)
    _other_event_keys = copy.copy(OTHER_EVENT_KEYS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = {}
        self._funcs = {}
        self._focus_listeners = set()
        self._focused_child_id = None
        self._parent = None
        self._layer = 0
        self._mouse_over = False
        self._element_position = (0,0)
        self._lock_input = set()
        for string in self._focus_event_keys + self._other_event_keys:
            try:
                self._funcs[string] = getattr(self, string)
            except AttributeError:
                pass
            try:
                newfunc = kwargs[string]
                try:
                    oldfunc = self._funcs[string]
                    def combinedfunc(*args, **kwargs): #create a pseudo super 
                        oldfunc()
                        newfunc()
                    self._funcs[string] = combinedfunc
                except KeyError:
                    self._funcs[string] = newfunc
            except KeyError:
                pass
        if self._funcs.keys() & (MOUSEENTER_KEY, MOUSELEAVE_KEY, MOUSEOVER_KEY): #if we have any of these
            self.addMouseMoveListener(self._mouseMove, priority = self.getEventListenerPriority)
        
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
    
    @property
    def parent(self):
        return self.getParent()
    @parent.setter
    def parent(self, *args, **kwargs):
        self.setParent(*args, **kwargs)
        
    @property
    def focus(self):
        return self.isFocused()
    @focus.setter
    def focus(self, *args, **kwargs):
        raise AttributeError("Cannot set focus directly. Set the parent's focused child instead.")
        
    def getLayer(self):
        return self._layer
    
    def setLayer(self, val):
        #should return the highest layer used by self and/or children
        self._layer = val
        self.setSpriteLayer(self._layer)
        return self.updateChildrenLayers()
        
    def updateChildrenLayers(self):
        #should return the highest used layer
        lastlayer = self.getLayer()
        for child in self.getAllChildren():
            lastlayer = child.setLayer(lastlayer + 1)
        return lastlayer
    
    def updateAllLayers(self):
        try: 
            self.getParent().updateAllLayers()
        except AttributeError:
            self.updateChildrenLayers() #only call this on top element
            
    def getMaxLayer(self):
        return max([self.getLayer(), *[child.getMaxLayer() for child in self.getAllChildren()]]) #put in list avoid typeerror if no children 
            
        
    def getParent(self):
        return unWeakRef(self._parent)
    
    def setParent(self, newparent):
        self._parent = weakRef(newparent)
        
    def setFocus(self, child):
        #pass None to clear focus
        try:
            ID = child.id
        except AttributeError:
            ID = child
        if ID != self._focused_child_id:
            oldfocus = self.getFocusedChild()
            if oldfocus:
                oldfocus._loseFocus()
            self._focused_child_id = ID
            if ID is not None:
                if ID in self._children:
                    self.getChild(ID)._gainFocus()
                else:
                    debugMessage("Probable error: child ID not found when setting focus: " + str(ID))
                    self._focused_child_id = None
        
    def clearFocus(self):
        #convenience function
        self.setFocus(None)
    
    def getFocusedChild(self):
        try:
            return self.getChild(self._focused_child_id)
        except KeyError:
            return None
        
    def isFocused(self):
        try:
            return self.getParent()._focused_child_id == self.id
        except AttributeError:
            return True #top level element always focused
        
    def isFullyFocused(self):
        if self.isFocused():
            parent = self.getParent()
            if parent:
                return parent.isFullyFocused()
            return True
        return False
        
    def hasFocusedChild(self):
        return self._focused_child_id != None
    
    def callEventFunc(self, key, *args, **kwargs):
        if self.hasEventFunc(key):
            return self._funcs[key](*args, **kwargs)
        return False
            
    def hasEventFunc(self, key):
        return key in self._funcs
    
    def getEventKey(self, key = ""):
        return str(self.id) + "_" + str(key) + "_EVENT"
    
    def getEventCaller(self, key, *args, **kwargs):
        #convenience function for delaying a custom event
        return lambda: customEvent(key, *args, **kwargs)
    
    def _activateConfirm(self, x = None, y = None):
        if self.isFullyFocused() and not self.isInputLocked():
            if not (x is not None and not self.checkPointWithinElement(x,y)): #weird pattern to avoid unnecessary evalution of second condition
                return self.callEventFunc(CONFIRM_KEY)
        return False
    
    def _activateConfirmHold(self, x = None, y = None):
        if self.isFullyFocused() and not self.isInputLocked():
            if not (x is not None and not self.checkPointWithinElement(x,y)): #weird pattern to avoid unnecessary evalution of second condition
                return self.callEventFunc(CONFIRMHOLD_KEY)
        return False
        
    def _activateCancel(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(CANCEL_KEY)
        return False
    
    def _activateCancelHold(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(CANCELHOLD_KEY)
        return False
        
    def _moveUp(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(MOVEUP_KEY)
        return False
    
    def _moveUpHold(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(MOVEUPHOLD_KEY)
        return False
        
    def _moveDown(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(MOVEDOWN_KEY)
        return False
    
    def _moveDownHold(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(MOVEDOWNHOLD_KEY)
        return False
        
    def _moveLeft(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(MOVELEFT_KEY)
        return False
    
    def _moveLeftHold(self):
        if self.focus and not self.isInputLocked():
            return self.callEventFunc(MOVELEFTHOLD_KEY)
        return False
        
    def _moveRight(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(MOVERIGHT_KEY)
        return False
    
    def _moveRightHold(self):
        if self.isFullyFocused() and not self.isInputLocked():
            return self.callEventFunc(MOVERIGHTHOLD_KEY)
        return False
    
    def _mouseMove(self, x, y, dx, dy):
        returnval = False
        inside = self.checkPointWithinElement(x, y)
        if not self._mouse_over and inside:
            returnval = self.callEventFunc(MOUSEENTER_KEY)
        if inside:
            self._mouse_over = True
            if not returnval:
                returnval = self.callEventFunc(MOUSEOVER_KEY, x, y, dx, dy)
        else:
            if not returnval and self._mouse_over:
                returnval = self.callEventFunc(MOUSELEAVE_KEY)
            self._mouse_over = False
        return returnval
    
    def isMousedOver(self):
        return self._mouse_over
    
    def setSelfFocused(self):
        #convenience function
        parent = self.getParent()
        if parent:
            parent.setFocus(self)
            
    def clearParentFocus(self):
        #convenience function
        parent = self.getParent()
        if parent:
            parent.setFocus(None)
            
    def _gainFocus(self):
        self.addFocusListeners()
        self.callEventFunc(GAINFOCUS_KEY)
            
    def _loseFocus(self):
        self.removeFocusListeners()
        self.callEventFunc(LOSEFOCUS_KEY)
            
    def addFocusListeners(self):
        if self.hasEventFunc(CONFIRM_KEY):
            self.addFocusListener(INPUT_EVENT_CONFIRM_UP, self._activateConfirm)
        if self.hasEventFunc(CONFIRMHOLD_KEY):
            self.addFocusListener(INPUT_EVENT_CONFIRM_HOLD, self._activateConfirmHold)
        if self.hasEventFunc(CANCEL_KEY):
            self.addFocusListener(INPUT_EVENT_CANCEL_UP, self._activateCancel)
        if self.hasEventFunc(CANCELHOLD_KEY):
            self.addFocusListener(INPUT_EVENT_CANCEL_HOLD, self._activateCancelHold)
        if self.hasEventFunc(MOVEUP_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_UP_UP, self._moveUp)
        if self.hasEventFunc(MOVEUPHOLD_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_UP_HOLD, self._moveUpHold)
        if self.hasEventFunc(MOVEDOWN_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_DOWN_UP, self._moveDown)
        if self.hasEventFunc(MOVEDOWNHOLD_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_DOWN_HOLD, self._moveDownHold)
        if self.hasEventFunc(MOVERIGHT_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_RIGHT_UP, self._moveRight)
        if self.hasEventFunc(MOVERIGHTHOLD_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_RIGHT_HOLD, self._moveRightHold)
        if self.hasEventFunc(MOVELEFT_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_LEFT_UP, self._moveLeft)
        if self.hasEventFunc(MOVELEFTHOLD_KEY):
            self.addFocusListener(INPUT_EVENT_MOVE_LEFT_HOLD, self._moveLeftHold)
    
    def addFocusListener(self, key, listener):
        self.addCustomListener(key, listener, priority = self.getEventListenerPriority)
        self._focus_listeners.add((key, listener))
        
    def removeFocusListeners(self):
        for key, listener in self._focus_listeners:
            self.removeCustomListener(key, listener)
        self._focus_listeners.clear()
    
    def getEventListenerPriority(self):
        return self.getLayer()

    def checkPointWithinElement(self, x, y):
        extents = self.getExtents()
        return extents[0] <= x <= extents[1] and extents[2] <= y <= extents[3]
    
    def setDimensions(self, x = None, y = None):
        if x is None: x = self.getWidth()
        if y is None: y = self.getHeight()
        self.setWidth(x)
        self.setHeight(y)

    def getDimensions(self):
        return self.getWidth(), self.getHeight()

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

    def setPosition(self, *args, **kwargs):
        '''alias for setPos'''
        self.setPos(*args, **kwargs)

    def shiftPosition(self, *args, **kwargs):
        '''alias for movePos'''
        self.movePos(*args, **kwargs)

    def addChild(self, newchild, update_layers = True):
        self._children[newchild.id] = newchild
        newchild.setParent(self)
        if update_layers:
            self.updateAllLayers()
        return newchild
    
    def getChild(self, child_id):
        try: return self._children[child_id]
        except (KeyError, TypeError):
            child_id = unWeakRef(child_id) #just in case weakref
            try: 
                child_id.id
            except AttributeError:
                raise KeyError("Child not found by ID: " + str(child_id))
            else:
                return child_id #probably an actual reference
            
    def removeChild(self, childid):
        child = self.getChild(childid) #cast to reference
        childid = child.id
        self._children.pop(childid, None)
        child.destroy()
        return childid
        
    def removeAllChildren(self):
        for child in list(self.getAllChildren()):
            self.removeChild(child)
        self._children.clear()
    
    def getAllChildren(self):
        return self._children.values()
    
    def getElementPosition(self):
        return self._element_position
    
    def setElementPosition(self, x = None, y = None):
        currentpos = self.getElementPosition()
        if x is None: x = currentpos[0]
        if y is None: y = currentpos[1]
        if x != currentpos[0] or y != currentpos[1]:
            self._element_position = (x,y)
            self._applyPosition()
        
    def moveElementPosition(self, x = 0, y = 0):
        self.setElementPosition(*map(operator.add, self.getElementPosition(), (x,y)))
    
    def getAnchorPoint(self):
        #returns origin point. overwrite if you want different behavior (bottom left, etc)
        return self.getPos()
    
    def getParentAnchorPoint(self):
        parent = self.getParent()
        if parent:
            return parent.getAnchorPoint()
        return (0,0)
    
    def _applyPosition(self):
        self.setPos(*map(operator.add, self.getElementPosition(), self.getParentAnchorPoint()))
            
    def _applyChildrenPositions(self):
        for child in self.getAllChildren():
            child._applyPosition()
            
    def lockInput(self, key = DEFAULT_INPUT_LOCK):
        self._lockInput(self.combineID(key))
        
    def _lockInput(self, key):
        self._lock_input.add(key)
        for child in self.getAllChildren():
            child._lockInput(key)
        
    def unlockInput(self, key = DEFAULT_INPUT_LOCK):
        self._unlockInput(self.combineID(key))
        
    def _unlockInput(self, key):
        self._lock_input.discard(key)
        for child in self.getAllChildren():
            child._unlockInput(key)
        
    def isInputLocked(self):
        return bool(self._lock_input)

    #overwritten stuff
    def setPos(self, *args, **kwargs):
        super().setPos(*args, **kwargs)
        self._applyChildrenPositions()
    
    def movePos(self, *args, **kwargs):
        super().movePos(*args, **kwargs)
        self._applyChildrenPositions()
    
    def sleep(self, *args, **kwargs):
        started_sleeping = super().sleep(*args, **kwargs)
        for child in self.getAllChildren():
            child.sleep(*args, **kwargs)
        return started_sleeping
            
    def wakeUp(self, *args, **kwargs):
        awoken = super().wakeUp(*args, **kwargs)
        for child in self.getAllChildren():
            child.wakeUp(*args, **kwargs)
        return awoken
        
    def destroy(self):
        super().destroy()
        self._funcs.clear()
        self.removeAllChildren()
        self.removeFocusListeners()
    
    
def _getRelevantMousePartitions(x_min, y_min, x_max, y_max):
    x_values = [x for x in range(x_min//MOUSE_PARTITION_SIZE_X, (x_max//MOUSE_PARTITION_SIZE_X)+1)]
    y_values = [y for y in range(y_min//MOUSE_PARTITION_SIZE_Y, (y_max//MOUSE_PARTITION_SIZE_Y)+1)]
    relevant_keys = [EVENT_MOUSE_MOVE_SECTION[(x, y)] for x in x_values for y in y_values]
    return relevant_keys

