from kaiengine.event import addCustomListener

from .interfaceElement import InterfaceElement
from .interfaceElementKeys import *
from .standardInterfaceElements import HorizontalContainer, VerticalContainer, SpriteElement, GridContainer, ContainerElement, StackContainer

_elements = {}

def _registerTopLevelElement(element, global_dict = _elements):
    global_dict[element.id] = element
    addCustomListener(element.id + EVENT_INTERFACE_DESTROYED, _unregisterTopLevelElement)

def _unregisterTopLevelElement(origin_id=None, global_dict = _elements):
    try:
        del global_dict[origin_id]
    except KeyError:
        pass

#TODO: make sure this happens late enough for the event system's liking
addCustomListener(EVENT_INTERFACE_TOP_LEVEL_ELEMENT_CREATED, _registerTopLevelElement)
