from kaiengine.event import customEvent
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
        if self.top_level:
            customEvent(EVENT_INTERFACE_TOP_LEVEL_ELEMENT_CREATED, self)

	@on_input(INPUT_EVENT_MOVE_UP)
	def respondMoveUp(self):
		self.event(EVENT_INTERFACE_FOCUS_SHIFT_UP)
		
	@on_input(INPUT_EVENT_MOVE_DOWN)
	def respondMoveDown(self):
		self.event(EVENT_INTERFACE_FOCUS_SHIFT_DOWN)
		
	@on_input(INPUT_EVENT_MOVE_LEFT)
	def respondMoveLeft(self):
		self.event(EVENT_INTERFACE_FOCUS_SHIFT_LEFT)
		
	@on_input(INPUT_EVENT_MOVE_RIGHT)
	def respondMoveRight(self):
		self.event(EVENT_INTERFACE_FOCUS_SHIFT_RIGHT)

    @property
    def focus_key(self):
        return self.inherited_focus_key or self.id

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

    def destroy(self):
        self.event(EVENT_INTERFACE_DESTROYED)
        super().destroy()
