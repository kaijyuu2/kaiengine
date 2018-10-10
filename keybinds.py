from kaiengine.settings import settings

#TODO: move constants/defaults to another file

INPUT_EVENT_TYPE_PRESS = "INPUT_EVENT_TYPE_PRESS"
INPUT_EVENT_TYPE_RELEASE = "INPUT_EVENT_TYPE_RELEASE"

INPUT_EVENT_CONFIRM = "INPUT_EVENT_CONFIRM"
INPUT_EVENT_CANCEL = "INPUT_EVENT_CANCEL"
INPUT_EVENT_MOVE_UP = "INPUT_EVENT_MOVE_UP"
INPUT_EVENT_MOVE_DOWN = "INPUT_EVENT_MOVE_DOWN"
INPUT_EVENT_MOVE_LEFT = "INPUT_EVENT_MOVE_LEFT"
INPUT_EVENT_MOVE_RIGHT = "INPUT_EVENT_MOVE_RIGHT"

BINDS = {
         (KAI_KEY_Z, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_CONFIRM,
         (KAI_KEY_ENTER, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_CONFIRM,
         (KAI_KEY_RETURN, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_CONFIRM,

         (KAI_KEY_X, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_CANCEL,
         (KAI_KEY_BACKSPACE, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_CANCEL,
         (KAI_KEY_SPACE, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_CANCEL,

         (KAI_KEY_W, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_UP,
         (KAI_KEY_UP, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_UP,
         (KAI_KEY_S, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_DOWN,
         (KAI_KEY_DOWN, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_DOWN,
         (KAI_KEY_A, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_LEFT,
         (KAI_KEY_LEFT, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_LEFT,
         (KAI_KEY_D, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_RIGHT,
         (KAI_KEY_RIGHT, INPUT_EVENT_TYPE_PRESS): INPUT_EVENT_MOVE_RIGHT
         }

def bindingResponse(event_type): #TODO: think of a better name
    def relayBinding(kai_key): #TODO: think of a better name
        try:
            bind = BINDS[(kai_key, event_type)] #TODO: correctly access binds via settings or whatever
        except KeyError:
            pass
        else:
            inputEvent(bind) #TODO: create inputEvent method (maybe?)
    return relayBinding

relayPress = bindingResponse(INPUT_EVENT_TYPE_PRESS)
relayRelease = bindingResponse(INPUT_EVENT_TYPE_RELEASE)

addKeyPressListener(relayPress)
addKeyReleaseListener(relayRelease)

addMousePressListener(relayPress)
addMouseReleaseListener(relayRelease)

#addJoybuttonPressListener(relayPress) #TODO: handle the 'joystick' argument issue
#addJoybuttonReleaseListener(relayRelease)

