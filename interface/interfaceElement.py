from kaiengine.event import customEvent
from kaiengine.keybinds import INPUT_EVENT_CONFIRM, INPUT_EVENT_CANCEL
from .interfaceElementEvent import EventIDInterface
from .interfaceElementKeys import *
from .interfaceMeta import _InterfaceElementMeta
from .screenElement import ScreenElement

class InterfaceElement(EventIDInterface, ScreenElement, metaclass=_InterfaceElementMeta):

    top_level = False

    def __init__(self, *args, **kwargs):
        super().__init__(self)
        self._init(*args, **kwargs)
        if self.top_level:
            customEvent(EVENT_INTERFACE_TOP_LEVEL_ELEMENT_CREATED, self)

    def _init(self, *args, **kwargs):
        pass

    def gainFocus(self):
        #clearCustomListeners(INPUT_EVENT_CONFIRM) #maybe..?
        #clearCustomListeners(INPUT_EVENT_CANCEL)
        self.addCustomListener(INPUT_EVENT_CONFIRM, self.activate)
        self.addCustomListener(INPUT_EVENT_CANCEL, self.cancel)

    def loseFocus(self):
        self.removeCustomListener(INPUT_EVENT_CONFIRM, self.activate)
        self.removeCustomListener(INPUT_EVENT_CANCEL, self.cancel)

    def activate(self):
        self.event(EVENT_INTERFACE_ACTIVATED)

    def cancel(self):
        pass

    def destroy(self):
        self.event(EVENT_INTERFACE_DESTROYED)
        super().destroy()
