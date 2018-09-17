from .interfaceElementEvent import EventIDInterface
from .interfaceElementKeys import *
from .interfaceMeta import _InterfaceElementMeta

class InterfaceElement(EventIDInterface, metaclass=_InterfaceElementMeta):

    def __init__(self, *args, **kwargs):
        super().__init__(self)
        self._init(*args, **kwargs)
        self.addCustomListener(self.ID + _EVENT_INTERFACE_REQUEST_SWITCH_MENU, self.replaceWith)

    def _init(self, *args, **kwargs):
        pass

    def activate(self):
        self.event(_EVENT_INTERFACE_ACTIVATED)

    def switchTo(self, element_class, *args):
        return (self.ID + _EVENT_INTERFACE_REQUEST_SWITCH_MENU, element_class, *args)


