
from collections import defaultdict

from kaiengine.destroyinterface import DestroyInterface

from kaiengine.event import *


class EventInterface(DestroyInterface):
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
        self._appendEventMethod(key, method)
        addCustomListener(key, method, priority)

    def removeCustomListener(self, key, method):
        self._removeEventMethod(key, method)

    def addKeyPressListener(self,listener, priority = 0):
        '''Register a function as a key press event listener.'''
        self._appendEventMethod(EVENT_KEY_PRESS, listener)
        addKeyPressListener(listener, priority)

    def removeKeyPressListener(self,listener):
        '''Unregister a key press event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_KEY_PRESS, listener)
        removeKeyPressListener(listener)

    def addKeyReleaseListener(self,listener, priority = 0):
        '''Register a function as a key release event listener.'''
        self._appendEventMethod(EVENT_KEY_RELEASE, listener)
        addKeyReleaseListener(listener, priority)

    def removeKeyReleaseListener(self,listener):
        '''Unregister a key release event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_KEY_RELEASE, listener)
        removeKeyReleaseListener(listener)

    def addMousePressListener(self,listener, priority = 0):
        '''Register a function as a mouse press event listener.'''
        self._appendEventMethod(EVENT_MOUSE_PRESS, listener)
        addMousePressListener(listener, priority)

    def removeMousePressListener(self,listener):
        '''Unregister a mouse press event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_MOUSE_PRESS, listener)
        removeMousePressListener(listener)

    def addMouseReleaseListener(self,listener, priority = 0):
        '''Register a function as a mouse release event listener.'''
        self._appendEventMethod(EVENT_MOUSE_RELEASE, listener)
        addMouseReleaseListener(listener, priority)

    def removeMouseReleaseListener(self,listener):
        '''Unregister a mouse release event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_MOUSE_RELEASE, listener)
        removeMouseReleaseListener(listener)

    def addMouseDragListener(self,listener, priority = 0):
        '''Register a function as a mouse drag event listener.'''
        self._appendEventMethod(EVENT_MOUSE_DRAG, listener)
        addMouseDragListener(listener, priority)

    def removeMouseDragListener(self,listener):
        '''Unregister a mouse drag event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_MOUSE_DRAG, listener)
        removeMouseDragListener(listener)

    def addMouseMoveListener(self,listener, priority = 0):
        '''Register a function as a mouse move event listener.'''
        self._appendEventMethod(EVENT_MOUSE_MOVE, listener)
        addMouseMoveListener(listener, priority)

    def removeMouseMoveListener(self,listener):
        '''Unregister a mouse move event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_MOUSE_MOVE, listener)
        removeMouseMoveListener(listener)

    def addMouseEnterListener(self,listener, priority=0):
        '''Register a function as a mouse enter window event listener.'''
        self._appendEventMethod(EVENT_MOUSE_ENTER, listener)
        addMouseEnterListener(listener, priority)

    def removeMouseEnterListener(self,listener):
        '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_MOUSE_ENTER, listener)
        removeMouseEnterListener(listener)

    def addMouseExitListener(self,listener, priority=0):
        '''Register a function as a mouse exit window event listener.'''
        self._appendEventMethod(EVENT_MOUSE_EXIT, listener)
        addMouseExitListener(listener, priority)

    def removeMouseExitListener(self,listener):
        '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
        self._removeEventMethod(EVENT_MOUSE_EXIT, listener)
        removeMouseExitListener(listener)

    def addJoybuttonPressListener(self,listener, priority = 0):
        self._appendEventMethod(EVENT_JOYPAD_PRESS, listener)
        addJoybuttonPressListener(listener, priority)

    def removeJoybuttonPressListener(self,listener):
        self._removeEventMethod(EVENT_JOYPAD_PRESS, listener)
        removeJoybuttonPressListener(listener)

    def addJoybuttonReleaseListener(self,listener, priority = 0):
        self._appendEventMethod(EVENT_JOYPAD_RELEASE, listener)
        addJoybuttonReleaseListener(listener, priority)

    def removeJoybuttonReleaseListener(self,listener):
        self._removeEventMethod(EVENT_JOYPAD_RELEASE, listener)
        removeJoybuttonReleaseListener(listener)

    def _appendEventMethod(self, key, method):
        self._event_methods[key].append(method)

    def _removeEventMethod(self, key, method):
        removeCustomListener(key, method)
        try: self._event_methods[key].remove(method)
        except (ValueError, KeyError) : pass


    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        if eventdriver is not None:
            for key, methods in list(self._event_methods.items()):
                for method in methods:
                    eventdriver._removeListener(key, method)
            for key in self._query_methods:
                eventdriver._removeQueryListener(key)
        self._event_methods.clear()
        self._query_methods.clear()
