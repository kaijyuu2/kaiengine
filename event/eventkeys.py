

#input
EVENT_KEY_PRESS = "_KEY_PRESS"
EVENT_KEY_RELEASE = "_KEY_RELEASE"
EVENT_MOUSE_PRESS = "_MOUSE_PRESS"
EVENT_MOUSE_RELEASE = "_MOUSE_RELEASE"
EVENT_MOUSE_MOVE = "_MOUSE_MOVE"
EVENT_MOUSE_DRAG = "_MOUSE_DRAG"
EVENT_JOYPAD_PRESS = "_JOYPAD_PRESS"
EVENT_JOYPAD_RELEASE = "_JOYPAD_RELEASE"
EVENT_GAME_CLOSE = "_GAME_CLOSE"
EVENT_MOUSE_ENTER = "_MOUSE_ENTER"
EVENT_MOUSE_EXIT = "_MOUSE_EXIT"

EVENT_INPUT_PREFIX = "_INPUT_EVENT_"
EVENT_REQUEST_LAYER_CREATION = "_CREATE_LAYER"
EVENT_LOCK_INPUT = "_LOCK_INPUT"
EVENT_REMOVE_INPUT_LOCKS = "_REMOVE_INPUT_LOCKS"
EVENT_FADE_IN = "_EVENT_FADE_IN"

#partitioned mouse movement
MOUSE_PARTITION_SIZE_X = 64
MOUSE_PARTITION_SIZE_Y = 64
MOUSE_PARTITION_COUNT_X = 32
MOUSE_PARTITION_COUNT_Y = 32
EVENT_MOUSE_MOVE_SECTION = dict([((x, y), "".join(("_MOUSE_MOVE_SECTION_", str(x), "_", str(y)))) for x in range(MOUSE_PARTITION_COUNT_X) for y in range(MOUSE_PARTITION_COUNT_Y)])
QUERY_MOUSE_MOVE_SECTION_BOUNDS = "_Q_MOUSE_MOVE_SECTION_BOUNDS_"
