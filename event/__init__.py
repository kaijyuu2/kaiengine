
import math

from . import eventdriver
from .eventkeys import *
from kaiengine.input import standardizedKey
from kaiengine.utilityFuncs import setMousePosition

_MOUSE_SECTION_CONNECTION_BUFFER = set()

def _initListener(self, event_key, func, priority, lock, sleep_when_unfocused):
    def instantiated(*args, **kwargs):
        if (not lock) or (not self._input_locks):
            return func(self, *args, **kwargs)
    if sleep_when_unfocused:
        self._input_listeners.append((event_key, instantiated, priority))
    else:
        self.addCustomListener(event_key, instantiated, priority)

def _initChildListener(self, child_key, event_key, func, priority, lock):
    child = getattr(self, child_key)
    event_key = child.id + event_key
    self._initListener(event_key, func, priority, lock, False)

class ListenerRegistryMeta(type):
    """Allow subclasses to independently define listeners to initialize.

    In order to allow for clean definition of event responses at the
    class level (e.g. decorator that makes a method be called on
    instances of that class in response to a specified event), this
    metaclass ensures that all subclasses of the class will maintain
    their own independent records of which listeners to initialize.
    Then, upon object initialization, it causes the new instance to
    hook those listeners.

    """

    def __init__(cls, *args, **kwargs):
        try:
            cls._listener_init = cls._listener_init[:]
        except AttributeError:
            cls._listener_init = []
        try:
            cls._child_listener_init = cls._child_listener_init[:]
        except AttributeError:
            cls._child_listener_init = []
        for key, attr in cls.__dict__.items():
            try:
                attr._listener_init_data
            except AttributeError:
                pass
            else:
                cls._listener_init.append((attr, *attr._listener_init_data))
            try:
                attr._child_listener_init_data
            except AttributeError:
                pass
            else:
                cls._child_listener_init.append((attr, attr._base_key, *attr._child_listener_init_data))
        cls._initListener = _initListener
        cls._initChildListener = _initChildListener
        return super().__init__(*args, **kwargs)


    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        obj._input_locks = set()
        obj._input_listeners = []
        try:
            p = kwargs["priority"]
        except:
            p = 0
        for func, event_key, priority, lock, sleep_when_unfocused in cls._listener_init:
            obj._initListener(event_key, func, priority or p, lock, sleep_when_unfocused)
        for func, child_key, event_key, priority, lock in cls._child_listener_init:
            obj._initChildListener(child_key, event_key, func, priority or p, lock)
        return obj

#custom events

def addCustomListener(key, listener, priority = 0):
    '''Register a function as a custom event listener'''
    eventdriver._addListener(key, listener, priority)

def removeCustomListener(key, listener):
    '''Unregister a function as a custom event listener'''
    eventdriver._removeListener(key, listener)

def clearCustomListeners(key):
    '''Unregister all functions as listeners for an event.'''
    eventdriver._clearListeners(key)

def addQueryListener(key, listener):
    eventdriver._addQueryListener(key, listener)

def removeQueryListener(key,*args, **kwargs): #listener unnecessary; just wanting to be symmetrical with regular listeners
    eventdriver._removeQueryListener(key, *args, **kwargs)

# input event registerers and deregisterers

def addKeyPressListener(listener, priority = 0):
    '''Register a function as a key press event listener.'''
    eventdriver._addListener(EVENT_KEY_PRESS, listener, priority)

def removeKeyPressListener(listener):
    '''Unregister a key press event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_KEY_PRESS, listener)

def addKeyReleaseListener(listener, priority = 0):
    '''Register a function as a key release event listener.'''
    eventdriver._addListener(EVENT_KEY_RELEASE, listener, priority)

def removeKeyReleaseListener(listener):
    '''Unregister a key release event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_KEY_RELEASE, listener)

def addMousePressListener(listener, priority = 0):
    '''Register a function as a mouse press event listener.'''
    eventdriver._addListener(EVENT_MOUSE_PRESS, listener, priority)

def removeMousePressListener(listener):
    '''Unregister a mouse press event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_MOUSE_PRESS, listener)

def addMouseReleaseListener(listener, priority = 0):
    '''Register a function as a mouse release event listener.'''
    eventdriver._addListener(EVENT_MOUSE_RELEASE, listener, priority)

def removeMouseReleaseListener(listener):
    '''Unregister a mouse release event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_MOUSE_RELEASE, listener)

def addMouseDragListener(listener, priority = 0):
    '''Register a function as a mouse drag event listener.'''
    eventdriver._addListener(EVENT_MOUSE_DRAG, listener, priority)

def removeMouseDragListener(listener):
    '''Unregister a mouse drag event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_MOUSE_DRAG, listener)

def addMouseMoveListener(listener, priority = 0):
    '''Register a function as a mouse move event listener.'''
    eventdriver._addListener(EVENT_MOUSE_MOVE, listener, priority)

def removeMouseMoveListener(listener):
    '''Unregister a mouse move event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_MOUSE_MOVE, listener)

def addSectionalMouseMoveListener(listener, priority=0, query_key=None):
    '''Queue a function for registration as a sectional mouse move event listener.'''
    _MOUSE_SECTION_CONNECTION_BUFFER.add((listener, priority, query_key))

def removeSectionalMouseMoveListener(listener):
    '''Unregister a sectional mouse move event listener.'''
    #TODO: implement
    pass

def addMouseEnterListener(listener, priority=0):
    '''Register a function as a mouse enter window event listener.'''
    eventdriver._addListener(EVENT_MOUSE_ENTER, listener, priority)

def removeMouseEnterListener(listener):
    '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_MOUSE_ENTER, listener)

def addMouseExitListener(listener, priority=0):
    '''Register a function as a mouse exit window event listener.'''
    eventdriver._addListener(EVENT_MOUSE_EXIT, listener, priority)

def removeMouseExitListener(listener):
    '''Unregister a mouse enter window event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_MOUSE_EXIT, listener)

def addJoybuttonPressListener(listener, priority = 0):
    eventdriver._addListener(EVENT_JOYPAD_PRESS, listener, priority)

def removeJoybuttonPressListener(listener):
    eventdriver._removeListener(EVENT_JOYPAD_PRESS, listener)

def addJoybuttonReleaseListener(listener, priority = 0):
    eventdriver._addListener(EVENT_JOYPAD_RELEASE, listener, priority)

def removeJoybuttonReleaseListener(listener):
    eventdriver._removeListener(EVENT_JOYPAD_RELEASE, listener)


# other event registerers

def addGameCloseListener(listener, priority = 0):
    '''Register a function for the game close event'''
    eventdriver._addListener(EVENT_GAME_CLOSE, listener, priority)

def removeGameCloseListener(listener):
    '''Unregister a game close event listener. Does nothing if listener is not actually listening.'''
    eventdriver._removeListener(EVENT_GAME_CLOSE, listener)




# event callers

def keyPressEvent(symbol):
    '''Process a key press event. If any listener returns True, halt processing.'''
    symbol = standardizedKey(symbol)
    eventdriver._callEvent(EVENT_KEY_PRESS, symbol)

def keyReleaseEvent(symbol):
    '''Process a key release event. If any listener returns True, halt processing.'''
    symbol = standardizedKey(symbol)
    eventdriver._callEvent(EVENT_KEY_RELEASE, symbol)

def mousePressEvent(x, y, button):
    '''Process a mouse press event. If any listener returns True, halt processing.'''
    button = standardizedKey(button)
    eventdriver._callEvent(EVENT_MOUSE_MOVE, x, y, 0, 0)
    eventdriver._callEvent(EVENT_MOUSE_PRESS, button, x, y)

def mouseReleaseEvent(x, y, button):
    '''Process a mouse release event. If any listener returns True, halt processing.'''
    button = standardizedKey(button)
    eventdriver._callEvent(EVENT_MOUSE_MOVE, x, y, 0, 0)
    eventdriver._callEvent(EVENT_MOUSE_RELEASE, button, x, y)

def mouseDragEvent(x, y, dx, dy, button):
    '''Process a mouse drag event. If any listener returns True, halt processing.'''
    button = standardizedKey(button)
    eventdriver._callEvent(EVENT_MOUSE_MOVE, x, y, dx, dy)
    eventdriver._callEvent(EVENT_MOUSE_DRAG, x, y, dx, dy, button)

def mouseMoveEvent(x,
                   y,
                   dx,
                   dy,
                   X_BLOCK_SIZE=MOUSE_PARTITION_SIZE_X,
                   Y_BLOCK_SIZE=MOUSE_PARTITION_SIZE_Y,
                   EVENT_MOUSE_MOVE_LOCALREF=EVENT_MOUSE_MOVE,
                   EVENT_MOUSE_MOVE_SECTION_LOCALREF=EVENT_MOUSE_MOVE_SECTION,
                   BUFFER_LOCALREF=_MOUSE_SECTION_CONNECTION_BUFFER):
    '''Process a mouse motion event. If any listener returns True, halt processing.'''
    #TODO: allow mixing global move events and sectional move events (currently, priority & returning True don't work as expected)
    for listener, priority, query_key in BUFFER_LOCALREF:
        x_min, x_max, y_min, y_max = callQuery(query_key)
        relevant_keys = [EVENT_MOUSE_MOVE_SECTION_LOCALREF[(x, y)]
                                                            for x in range(int(x_min//X_BLOCK_SIZE), int((x_max//X_BLOCK_SIZE))+1)
                                                            for y in range(int(y_min//Y_BLOCK_SIZE), int((y_max//Y_BLOCK_SIZE))+1)]
        for event_key in relevant_keys:
            eventdriver._addListener(event_key, listener, priority)
    BUFFER_LOCALREF.clear()
    eventdriver._callEvent(EVENT_MOUSE_MOVE_LOCALREF, x, y, dx, dy)
    eventdriver._callEvent(EVENT_MOUSE_MOVE_SECTION_LOCALREF[(int(x//X_BLOCK_SIZE), int(y//Y_BLOCK_SIZE))], x, y, dx, dy)

def joybuttonPressEvent(joystick, button):
    '''Process a controller press event. If any listener returns True, halt processing.'''
    eventdriver._callEvent(EVENT_JOYPAD_PRESS, joystick, button)

def joybuttonReleaseEvent(joystick, button):
    '''Process a controller press event. If any listener returns True, halt processing.'''
    eventdriver._callEvent(EVENT_JOYPAD_RELEASE, joystick, button)

def mouseEnterEvent(x, y):
    '''Process a mouse enter window event. If any listener returns True, halt processing.'''
    eventdriver._callEvent(EVENT_MOUSE_ENTER, x, y)

def mouseExitEvent(x, y):
    '''Process a mouse exit window event. If any listener returns True, halt processing.'''
    eventdriver._callEvent(EVENT_MOUSE_EXIT, x, y)

def gameCloseEvent():
    '''Process a game close event. If any listener returns True, halt processing.'''
    eventdriver._callEvent(EVENT_GAME_CLOSE)

def customEvent(key, *args, **kwargs):
    '''Call a custom event'''
    eventdriver._callEvent(key, *args, **kwargs)

def callQuery(key, *args, **kwargs):
    return eventdriver._callQuery(key, *args, **kwargs)


addMouseMoveListener(setMousePosition, math.inf)
