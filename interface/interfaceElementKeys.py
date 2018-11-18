ACTIVATE_APPEND = "ResponseActivate"

EVENT_INTERFACE_ACTIVATED = "_E_I_ACTIVATED"
EVENT_INTERFACE_DESTROYED = "_E_I_DESTROYED"
EVENT_INTERFACE_TOP_LEVEL_ELEMENT_CREATED = "_E_I_TOP_LEVEL_CREATED"
EVENT_INTERFACE_GAIN_FOCUS = "_E_I_GAIN_FOCUS"

DIRECTION_DOWN = "down"
DIRECTION_UP = "up"
DIRECTION_RIGHT = "right"
DIRECTION_LEFT = "left"

EVENT_INTERFACE_FOCUS_SHIFT_UP = "_E_I_FOCUS_SHIFT_UP"
EVENT_INTERFACE_FOCUS_SHIFT_DOWN = "_E_I_FOCUS_SHIFT_DOWN"
EVENT_INTERFACE_FOCUS_SHIFT_LEFT = "_E_I_FOCUS_SHIFT_LEFT"
EVENT_INTERFACE_FOCUS_SHIFT_RIGHT = "_E_I_FOCUS_SHIFT_RIGHT"
EVENT_INTERFACE_FOCUS_SHIFT = {DIRECTION_DOWN: EVENT_INTERFACE_FOCUS_SHIFT_DOWN,
                               DIRECTION_UP: EVENT_INTERFACE_FOCUS_SHIFT_UP,
                               DIRECTION_LEFT: EVENT_INTERFACE_FOCUS_SHIFT_LEFT,
                               DIRECTION_RIGHT: EVENT_INTERFACE_FOCUS_SHIFT_RIGHT}
