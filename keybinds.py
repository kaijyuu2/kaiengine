from kaiengine.gconfig import *

from kaiengine.event import customEvent, addKeyPressListener, addKeyReleaseListener, addMousePressListener, addMouseReleaseListener
from kaiengine.settings import settings
from kaiengine.timer import schedule, unschedule

from kaiengine.input.keys import *

_held_keys = set()

def createBindingRelayer(event_type, hold_func):
    def relayBinding(kai_key, *args, **kwargs):
        binds = settings.getValue(DYNAMIC_SETTINGS_KEY_BINDS)
        try:
            bind = binds[(kai_key + event_type)]
        except KeyError:
            pass
        else:
            hold_func(kai_key)
            customEvent(bind, *args, **kwargs)
    return relayBinding

def _fireHeldKeyEvents():
    binds = settings.getValue(DYNAMIC_SETTINGS_KEY_BINDS)
    for key in _held_keys:
        try:
            bind = binds[key]
        except KeyError:
            pass
        else:
            customEvent(bind)

def startHeld(kai_key):
    if len(_held_keys) == 0:
        schedule(_fireHeldKeyEvents, 1, True)
    _held_keys.add(kai_key + INPUT_EVENT_TYPE_HOLD)
    
def endHeld(kai_key):
    _held_keys.discard(kai_key)
    if len(_held_keys) == 0:
        unschedule(_fireHeldKeyEvents)

relayPress = createBindingRelayer(INPUT_EVENT_TYPE_PRESS, startHeld)
relayRelease = createBindingRelayer(INPUT_EVENT_TYPE_RELEASE, endHeld)
    

addKeyPressListener(relayPress)
addKeyReleaseListener(relayRelease)

addMousePressListener(relayPress)
addMouseReleaseListener(relayRelease)

#addJoybuttonPressListener(relayPress) #TODO: handle the 'joystick' argument issue
#addJoybuttonReleaseListener(relayRelease)

