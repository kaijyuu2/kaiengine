
from collections import defaultdict

from kaiengine.destroyinterface import DestroyInterface
from .sleep_interface import SleepInterface

from kaiengine.event import *


class EventInterface(DestroyInterface, SleepInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event_methods = defaultdict(list)
        self._query_methods = defaultdict(list)

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
        except (IndexError, KeyError):
            pass

    def addKeyPressListener(self,*args, **kwargs):
        '''Register a function as a key press event listener.'''
        self.addCustomListener(EVENT_KEY_PRESS, *args, **kwargs)

    def removeKeyPressListener(self,*args, **kwargs):
        '''Unregister a key press event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_KEY_PRESS, *args, **kwargs)

    def addKeyReleaseListener(self,listener, priority = 0):
        '''Register a function as a key release event listener.'''
        self.addCustomListener(EVENT_KEY_RELEASES, *args, **kwargs)

    def removeKeyReleaseListener(self,listener):
        '''Unregister a key release event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_KEY_RELEASE, *args, **kwargs)

    def addMousePressListener(self,listener, priority = 0):
        '''Register a function as a mouse press event listener.'''
        self.addCustomListener(EVENT_MOUSE_PRESS, *args, **kwargs)

    def removeMousePressListener(self,listener):
        '''Unregister a mouse press event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_PRESS, *args, **kwargs)

    def addMouseReleaseListener(self,listener, priority = 0):
        '''Register a function as a mouse release event listener.'''
        self.addCustomListener(EVENT_MOUSE_RELEASE, *args, **kwargs)

    def removeMouseReleaseListener(self,listener):
        '''Unregister a mouse release event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_RELEASE, *args, **kwargs)

    def addMouseDragListener(self,listener, priority = 0):
        '''Register a function as a mouse drag event listener.'''
        self.addCustomListener(EVENT_MOUSE_DRAG, *args, **kwargs)

    def removeMouseDragListener(self,listener):
        '''Unregister a mouse drag event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_DRAG, *args, **kwargs)

    def addMouseMoveListener(self,listener, priority = 0):
        '''Register a function as a mouse move event listener.'''
        self.addCustomListener(EVENT_MOUSE_MOVE, *args, **kwargs)

    def removeMouseMoveListener(self,listener):
        '''Unregister a mouse move event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_MOVE, *args, **kwargs)

    def addMouseEnterListener(self,listener, priority=0):
        '''Register a function as a mouse enter window event listener.'''
        self.addCustomListener(EVENT_MOUSE_ENTER, *args, **kwargs)

    def removeMouseEnterListener(self,listener):
        '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_ENTER, *args, **kwargs)

    def addMouseExitListener(self,listener, priority=0):
        '''Register a function as a mouse exit window event listener.'''
        self.addCustomListener(EVENT_MOUSE_EXIT, *args, **kwargs)

    def removeMouseExitListener(self,listener):
        '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
        self.removeCustomListener(EVENT_MOUSE_EXIT, *args, **kwargs)

    def addJoybuttonPressListener(self,listener, priority = 0):
        self.addCustomListener(EVENT_JOYPAD_PRESS, *args, **kwargs)

    def removeJoybuttonPressListener(self,listener):
        self.removeCustomListener(EVENT_JOYPAD_PRESS, *args, **kwargs)

    def addJoybuttonReleaseListener(self,listener, priority = 0):
        self.addCustomListener(EVENT_JOYPAD_RELEAS, *args, **kwargs)

    def removeJoybuttonReleaseListener(self,listener):
        self.removeCustomListener(EVENT_JOYPAD_RELEAS, *args, **kwargs)
        
    def removeAllListeners(self):
        self._removeAllListeners()
        self._event_methods.clear()
        self._query_methods.clear()
        
    def _removeAllListeners(self):
        for key, methoddata in self._event_methods.items():
            for method, priority in methoddata:
                removeCustomListener(key, method)
        for key in self._query_methods:
            removeQueryListener(key)

    #overwritten stuff
    def sleep(self, *args, **kwargs):
        super().sleep(*args, **kwargs)
        self._removeAllListeners() #don't remove them from local dictionaries, in case we wake up later
    
    def wakeUp(self, *args, **kwargs):
        super().wakeUp(*args, **kwargs)
        for key, methoddata in self._event_methods.items():
            for method, priority in methoddata:
                addCustomListener(key, method, priority)
        for key, query in self._query_methods.items():
            addQueryListener(key, query)
        

    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        self.removeAllListeners()
