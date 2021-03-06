# -*- coding: utf-8 -*-

from kaiengine.gconfig import *

CONFIRM_KEY = "confirm"
CONFIRMHOLD_KEY = "confirmhold"
CANCEL_KEY = "cancel"
CANCELHOLD_KEY = "cancelhold"
MOVEUP_KEY = "moveup"
MOVEUPHOLD_KEY = "moveuphold"
MOVEDOWN_KEY = "movedown"
MOVEDOWNHOLD_KEY = "movedownhold"
MOVERIGHT_KEY = "moveright"
MOVERIGHTHOLD_KEY = "moverighthold"
MOVELEFT_KEY = "moveleft"
MOVELEFTHOLD_KEY = "movelefthold"
MOUSEENTER_KEY = "mouseenter"
MOUSEOVER_KEY = "mouseover"
MOUSELEAVE_KEY = "mouseleave"
GAINFOCUS_KEY = "gainfocus"
LOSEFOCUS_KEY = "losefocus"

OTHER_EVENT_KEYS = (MOUSEENTER_KEY, MOUSEOVER_KEY, MOUSELEAVE_KEY, GAINFOCUS_KEY, LOSEFOCUS_KEY)

KEYBIND_MAP = {CONFIRM_KEY: [INPUT_EVENT_CONFIRM_UP],
               CONFIRMHOLD_KEY: [INPUT_EVENT_CONFIRM_HOLD],
               CANCEL_KEY: [INPUT_EVENT_CANCEL_UP],
               CANCELHOLD_KEY: [INPUT_EVENT_CANCEL_HOLD],
               MOVEUP_KEY: [INPUT_EVENT_MOVE_UP_UP],
               MOVEUPHOLD_KEY: [INPUT_EVENT_MOVE_UP_HOLD],
               MOVEDOWN_KEY: [INPUT_EVENT_MOVE_DOWN_UP],
               MOVEDOWNHOLD_KEY: [INPUT_EVENT_MOVE_DOWN_HOLD],
               MOVELEFT_KEY: [INPUT_EVENT_MOVE_LEFT_UP],
               MOVELEFTHOLD_KEY: [INPUT_EVENT_MOVE_LEFT_HOLD],
               MOVERIGHT_KEY: [INPUT_EVENT_MOVE_RIGHT_UP],
               MOVERIGHTHOLD_KEY: [INPUT_EVENT_MOVE_RIGHT_HOLD]}
