from kaiengine.gconfig import *

from kaiengine.event import customEvent, callQuery, MOUSE_PARTITION_SIZE_X, MOUSE_PARTITION_SIZE_Y, EVENT_MOUSE_MOVE_SECTION
from kaiengine.keybinds import INPUT_EVENT_CONFIRM, INPUT_EVENT_CANCEL
from kaiengine.objectinterface import EventInterface, GraphicInterface, PositionInterface

from .interfaceElementKeys import *
from .interfaceMeta import _InterfaceElementMeta


def getRelevantMousePartitions(x_min, y_min, x_max, y_max):
    x_values = [x for x in range(x_min//MOUSE_PARTITION_SIZE_X, (x_max//MOUSE_PARTITION_SIZE_X)+1)]
    y_values = [y for y in range(y_min//MOUSE_PARTITION_SIZE_Y, (y_max//MOUSE_PARTITION_SIZE_Y)+1)]
    relevant_keys = [EVENT_MOUSE_MOVE_SECTION[(x, y)] for x in x_values for y in y_values]
    return relevant_keys


class InterfaceElement(EventInterface, GraphicInterface, metaclass=_InterfaceElementMeta):

    can_have_focus = False
    focus_group = None

    def __init__(self, top_level = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setLayer(self, *args, **kwargs):
        super().setSpriteLayer(*args, **kwargs)

    @property
    def height(self):
        return self.getSpriteHeight() or 0

    @property
    def width(self):
        return self.getSpriteWidth() or 0

    def _applyPosition(self):
        super()._applyPosition()
        self._updateSpritePos()

    def setSprite(self, *args, **kwargs):
        super().setSprite(*args, **kwargs)
        self._applyPosition()


class InteractiveElement(InterfaceElement):

    can_have_focus = True


class TextButtonElement(InteractiveElement):

    frame = None

    def __init__(self, text="DEBUG", *args, **kwargs):
        super().__init__(*args, **kwargs)


class InterfaceContainer(InterfaceElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = {}
        self._child_locations = {}
        for arg in *args:
            self.addChild(arg)

    @property
    def child_locations(self):
        return sorted([(child_id, location) for child_id, location in self._child_locations.items()], key=lambda x: x[1])

    def nextDefaultLocation(self):
        return len(self._child_locations)

    def calculateChildPosition(self, child):
        return self.position

    def addChild(self, child, location=None):
        self._children[child.id] = child
        self._child_locations[child.id] = location or self.nextDefaultLocation()


class StackContainer(InterfaceContainer):

    pass


class VerticalContainer(InterfaceContainer):

    def calculateChildPosition(self, child):
        locations = self.child_locations
        child_location_index = locations.index(child.id)
        preceding_height = sum([self._children[child_id].height for child_id in locations[:child_location_index]])
        return self.position + [0, preceding_height]

class HorizontalContainer(InterfaceContainer):

    def calculateChildPosition(self, child):
        locations = self.child_locations
        child_location_index = locations.index(child.id)
        preceding_width = sum([self._children[child_id].width for child_id in locations[:child_location_index]])
        return self.position + [preceding_width, 0]

class GridContainer(InterfaceContainer):

    @property
    def grid_size(self):
        try:
            first_child = list(self._children.values())[0]
            return (first_child.width, first_child.height)
        except IndexError:
            return (0, 0)

    def nextDefaultLocation(self):
        return (len(self._child_locations), len(self._child_locations))

    def calculateChildPosition(self, child):
        location = self._child_locations(child.id)
        return self.position + (self.grid_size[0] * location[0], self.grid_size[1] * location[1])


class GenericMenu(StackContainer):

    frame_style = None
    internal_container_type = InterfaceContainer

    def __init__(self, *args, **kwargs):
        super().__init__(self, **kwargs)
        if self.frame_style:
            self.frame = self.addChild(FrameElement, 0)
        self.menu_options = self.addChild(internal_container_type(*args), 1)

class VerticalMenu(GenericMenu):

    internal_container_type = VerticalContainer

class HorizontalMenu(GenericMenu):

    internal_container_type = HorizontalContainer
