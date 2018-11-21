from kaiengine.gconfig import *
from kaiengine.event import customEvent, callQuery
from kaiengine.keybinds import INPUT_EVENT_CONFIRM, INPUT_EVENT_CANCEL
from .interfaceElementEvent import EventIDInterface
from .interfaceElementKeys import *
from .interfaceMeta import _InterfaceElementMeta
from .screenElement import ScreenElement

class InterfaceElement(EventIDInterface, ScreenElement, metaclass=_InterfaceElementMeta):

    top_level = False
    interactive = False
    inherited_focus_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(self)
        if self.interactive:
            self.addCustomListener(EVENT_INTERFACE_GAIN_FOCUS + self.focus_key, self.focusChanged)
        self._init(*args, **kwargs)
        self.connectChildren()
        if self.top_level:
            customEvent(EVENT_INTERFACE_TOP_LEVEL_ELEMENT_CREATED, self)

    @property
    def focus_key(self):
        return self.inherited_focus_key or self.id

    def _shiftFocus(direction):
        def func(self, position_hint=None, **kwargs):
            callQuery(self.id + EVENT_INTERFACE_FOCUS_SHIFT[direction], source_direction=direction, position_hint=position_hint or self.position)
        return func

    shiftFocusUp = _shiftFocus(DIRECTION_UP)
    shiftFocusDown = _shiftFocus(DIRECTION_DOWN)
    shiftFocusLeft = _shiftFocus(DIRECTION_LEFT)
    shiftFocusRight = _shiftFocus(DIRECTION_RIGHT)

    @on_input(INPUT_EVENT_MOVE_UP)
    def respondMoveUp(self):
        self.shiftFocusUp()

    @on_input(INPUT_EVENT_MOVE_DOWN)
    def respondMoveDown(self):
        self.shiftFocusDown()

    @on_input(INPUT_EVENT_MOVE_LEFT)
    def respondMoveLeft(self):
        self.shiftFocusLeft()

    @on_input(INPUT_EVENT_MOVE_RIGHT)
    def respondMoveRight(self):
        self.shiftFocusRight()

    @property
    def interactive_children(self):
        return [child for child in self.children if child.interactive]

    def inheritFocusKey(self, key):
        self.removeCustomListener(EVENT_INTERFACE_GAIN_FOCUS + self.focus_key, self.focusChanged)
        self.inherited_focus_key = key
        self.addCustomListener(EVENT_INTERFACE_GAIN_FOCUS + self.focus_key, self.focusChanged)

    def _init(self, *args, **kwargs):
        pass

    def activate(self):
        self.event(EVENT_INTERFACE_ACTIVATED)

    def cancel(self):
        pass

    def acceptFocus(self, source_direction=None, position_hint=None):
        self._gainFocus()

    def _gainFocus(self):
        self.gainFocus()
        for event_key, func, priority in self._input_listeners:
            self.addCustomListener(event_key, func, priority)
        customEvent(EVENT_INTERFACE_GAIN_FOCUS + self.focus_key, self.id)

    def gainFocus(self):
        pass

    def _loseFocus(self):
        self.loseFocus()
        for event_key, func, priority in self._input_listeners:
            self.removeCustomListener(event_key, func)

    def loseFocus(self):
        pass

    def focusChanged(self, element_id):
        if element_id != self.id:
            self.loseFocus()

    def addChild(self, child_element, *args, **kwargs):
        child_element.inheritFocusKey(self.focus_key)
        return super().addChild(child_element, *args, **kwargs)

    def connectChildren(self):
        pass

    def destroy(self):
        self.event(EVENT_INTERFACE_DESTROYED)
        super().destroy()
