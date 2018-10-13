from kaiengine.gconfig import *

from kaiengine.event import customEvent, addKeyPressListener, addKeyReleaseListener, addMousePressListener, addMouseReleaseListener
from kaiengine.settings import settings

from kaiengine.input.keys import *

def createBindingRelayer(event_type):
    def relayBinding(kai_key):
        binds = settings.getValue(DYNAMIC_SETTINGS_KEY_BINDS)
        try:
            bind = binds[(kai_key + event_type)]
        except KeyError:
            pass
        else:
            customEvent(bind)
    return relayBinding

relayPress = createBindingRelayer(INPUT_EVENT_TYPE_PRESS)
relayRelease = createBindingRelayer(INPUT_EVENT_TYPE_RELEASE)

addKeyPressListener(relayPress)
addKeyReleaseListener(relayRelease)

addMousePressListener(relayPress)
addMouseReleaseListener(relayRelease)

#addJoybuttonPressListener(relayPress) #TODO: handle the 'joystick' argument issue
#addJoybuttonReleaseListener(relayRelease)

