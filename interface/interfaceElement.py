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

    def _init(self, *args, **kwargs):
        pass

    def activate(self):
        self.event(EVENT_INTERFACE_ACTIVATED)

    def destroy(self):
        self.event(EVENT_INTERFACE_DESTROYED)
        super().destroy()

    #if SELF.INTERACTABLE: connect to confirm, etc.?
    #only the "focus" one should get confrim/cancel/etc
    #move (mouse incl) should be handled by changing focus
