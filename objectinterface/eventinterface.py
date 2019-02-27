
from collections import defaultdict

from kaiengine.uidgen import IdentifiedObject
from kaiengine.destroyinterface import DestroyInterface

from .sleep_interface import SleepInterface

from kaiengine.event import *


class EventInterface(SleepInterface, IdentifiedObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event_methods = defaultdict(list)
        self._query_methods = {}
        self._sleeplessKeys = set()
        
    def callIDEvent(self, event_key, *args, **kwargs):
        customEvent(self.getEventID(event_key), self.id, *args, **kwargs)
        
    def getEventID(self, event_key):
        return self.id + event_key

    def addQueryListener(self, key, method):
        self.removeQueryListener(self, key)
        self._query_methods[key] = method
        addQueryListener(key, method)

    def removeQueryListener(self, key, *args, **kwargs):
        try: del self._query_methods[key]
        except KeyError: pass
        removeQueryListener(key, *args, **kwargs)

    def addCustomListener(self,key, method, priority = 0):
        self._event_methods[key].append((method, priority))
        if not self.sleeping:
            addCustomListener(key, method, priority)

    def removeCustomListener(self, key, method):
        removeCustomListener(key, method)
        index = -1
        try:
            for i, data in enumerate(self._event_methods[key]):
                if data[0] == method:
                    index = i
                    break
            if index >= 0:
                del self._event_methods[key][i]
            if not self._event_methods[key]:
                del self._event_methods[key]
        except (IndexError, KeyError):
            pass

    def addKeyPressListener(self,*args, **kwargs):
        '''Register a function as a key press event listener.'''
        self.addCustomListener(EVENT_KEY_PRESS, *args, **kwargs)

    def removeKeyPressListener(self,*args, **kwargs):
        '''Unregister a key press event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_KEY_PRESS, *args, **kwargs)

    def addKeyReleaseListener(self,*args, **kwargs):
        '''Register a function as a key release event listener.'''
        self.addCustomListener(EVENT_KEY_RELEASE, *args, **kwargs)

    def removeKeyReleaseListener(self,*args, **kwargs):
        '''Unregister a key release event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_KEY_RELEASE, *args, **kwargs)

    def addMousePressListener(self,*args, **kwargs):
        '''Register a function as a mouse press event listener.'''
        self.addCustomListener(EVENT_MOUSE_PRESS, *args, **kwargs)

    def removeMousePressListener(self,*args, **kwargs):
        '''Unregister a mouse press event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_PRESS, *args, **kwargs)

    def addMouseReleaseListener(self,*args, **kwargs):
        '''Register a function as a mouse release event listener.'''
        self.addCustomListener(EVENT_MOUSE_RELEASE, *args, **kwargs)

    def removeMouseReleaseListener(self,*args, **kwargs):
        '''Unregister a mouse release event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_RELEASE, *args, **kwargs)

    def addMouseDragListener(self,*args, **kwargs):
        '''Register a function as a mouse drag event listener.'''
        self.addCustomListener(EVENT_MOUSE_DRAG, *args, **kwargs)

    def removeMouseDragListener(self,*args, **kwargs):
        '''Unregister a mouse drag event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_DRAG, *args, **kwargs)

    def addMouseMoveListener(self,*args, **kwargs):
        '''Register a function as a mouse move event listener.'''
        self.addCustomListener(EVENT_MOUSE_MOVE, *args, **kwargs)

    def removeMouseMoveListener(self,*args, **kwargs):
        '''Unregister a mouse move event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_MOVE, *args, **kwargs)

    def addMouseEnterListener(self,*args, **kwargs):
        '''Register a function as a mouse enter window event listener.'''
        self.addCustomListener(EVENT_MOUSE_ENTER, *args, **kwargs)

    def removeMouseEnterListener(self,*args, **kwargs):
        '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_ENTER, *args, **kwargs)

    def addMouseExitListener(self,*args, **kwargs):
        '''Register a function as a mouse exit window event listener.'''
        self.addCustomListener(EVENT_MOUSE_EXIT, *args, **kwargs)

    def removeMouseExitListener(self,*args, **kwargs):
        '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_EXIT, *args, **kwargs)

    def addJoybuttonPressListener(self,*args, **kwargs):
        self.addCustomListener(EVENT_JOYPAD_PRESS, *args, **kwargs)

    def removeJoybuttonPressListener(self,*args, **kwargs):
        self.removeCustomListener(EVENT_JOYPAD_PRESS, *args, **kwargs)

    def addJoybuttonReleaseListener(self,*args, **kwargs):
        self.addCustomListener(EVENT_JOYPAD_RELEASE, *args, **kwargs)

    def removeJoybuttonReleaseListener(self,*args, **kwargs):
        self.removeCustomListener(EVENT_JOYPAD_RELEASE, *args, **kwargs)
        
    def removeAllListeners(self):
        self._removeAllListeners()
        self._event_methods.clear()
        self._query_methods.clear()
        
    def _removeAllListeners(self):
        for key, methoddata in self._event_methods.items():
            if key not in self._sleeplessKeys:
                for method, priority in methoddata:
                    removeCustomListener(key, method)
        for key in self._query_methods:
            if key not in self._sleeplessKeys:
                removeQueryListener(key)

    #overwritten stuff
    def sleep(self, ignored_keys = (), *args, **kwargs):
        startedsleeping = super().sleep(*args, **kwargs)
        if startedsleeping:
            self._sleeplessKeys = self._sleeplessKeys.union(ignored_keys)
            self._removeAllListeners(ignored_keys) #don't remove them from local dictionaries, in case we wake up later
        return startedsleeping
    
    def wakeUp(self, *args, **kwargs):
        previouslysleeping = super().wakeUp(*args, **kwargs)
        if previouslysleeping:
            self._sleeplessKeys = set()
            for key, methoddata in self._event_methods.items():
                for method, priority in methoddata:
                    addCustomListener(key, method, priority)
            for key, query in self._query_methods.items():
                addQueryListener(key, query)
        return previouslysleeping
        

    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        self.removeAllListeners()
