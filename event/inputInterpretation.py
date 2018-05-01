from kaiengine.event.eventdriver import _addListener, _callEvent
from kaiengine.event.eventkeys import EVENT_INPUT_PREFIX, EVENT_KEY_PRESS, EVENT_MOUSE_PRESS, EVENT_JOYPAD_PRESS
from kaiengine.keybinds import keyName

def _relayInputEventKey(symbol, modifiers):
    bind = keyName(symbol)
    if bind:
        _callEvent(EVENT_INPUT_PREFIX + str(bind))

def _relayInputEventMouse(x, y, button, modifiers):
    bind = keyName(button)
    if bind:
        _callEvent(EVENT_INPUT_PREFIX + str(bind))

def initializeGlue():
    _addListener(EVENT_KEY_PRESS, _relayInputEventKey, 0)
    _addListener(EVENT_MOUSE_PRESS, _relayInputEventMouse, 0)
    #_addListener(EVENT_JOYPAD_PRESS, _relayInputEvent, 0)