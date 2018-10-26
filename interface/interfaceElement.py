from kaiengine.event import customEvent
from kaiengine.keybinds import INPUT_EVENT_CONFIRM, INPUT_EVENT_CANCEL
from .interfaceElementEvent import EventIDInterface
from .interfaceElementKeys import *
from .interfaceMeta import _InterfaceElementMeta
from .screenElement import ScreenElement

class InterfaceElement(EventIDInterface, ScreenElement, metaclass=_InterfaceElementMeta):

    top_level = False
    inherited_focus_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(self)
        self.addCustomListener(EVENT_INTERFACE_GAIN_FOCUS + self.focus_key, self.focusChanged)
        self._init(*args, **kwargs)
        if self.top_level:
            customEvent(EVENT_INTERFACE_TOP_LEVEL_ELEMENT_CREATED, self)

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

    def gainFocus(self):
        customEvent(EVENT_INTERFACE_GAIN_FOCUS + self.focus_key, self.id)

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
