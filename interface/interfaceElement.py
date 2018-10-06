from kaiengine.event import customEvent
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
        self.addCustomListener(self.id + EVENT_INTERFACE_REQUEST_SWITCH_MENU, self.replaceWith)

    def _init(self, *args, **kwargs):
        pass

    def replaceWith(self, *args, **kwargs):
        pass

    def activate(self):
        self.event(EVENT_INTERFACE_ACTIVATED)

    def switchTo(self, element_class, *args):
        return (self.id + EVENT_INTERFACE_REQUEST_SWITCH_MENU, element_class, *args)

    def destroy(self):
        self.event(EVENT_INTERFACE_DESTROYED)
        super().destroy()
