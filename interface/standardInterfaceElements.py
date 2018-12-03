from .interfaceElement import InterfaceElement
from .interfaceElementKeys import *

from kaiengine.display import createGraphic
from kaiengine.event import addQueryListener
from kaiengine.safeminmax import dmax

class HorizontalContainer(InterfaceElement):

    #TODO: allow location-based positioning

    spacing = 0

    @property
    def interactive(self):
        #TODO: fix the logic here in a better way
        return self.interactive_children

    def _childPosition(self, child_id):
        index = list(self._children.keys()).index(child_id)
        offset = sum([child.width + self.spacing for child in list(self.children)[:index]])
        return self._position + (offset, 0)

    def _calculateWidth(self):
        return max(0, sum([child.width + self.spacing for child in self.children]) - self.spacing)

    def closestInteractiveChild(self, position_hint):
        #TODO: improve implementation
        try:
            x = position_hint[0]
        except TypeError:
            return self.interactive_children[0]
        else:
            for child in self.interactive_children:
                if child.position[0] >= x:
                    return child
        return self.interactive_children[0]

    def acceptFocus(self, source_direction=None, position_hint=None):
        if source_direction in (DIRECTION_DOWN, DIRECTION_UP):
            self.closestInteractiveChild(position_hint).acceptFocus(source_direction=source_direction, position_hint=position_hint)
        elif source_direction == DIRECTION_RIGHT:
            self.interactive_children[0].acceptFocus(source_direction=source_direction, position_hint=position_hint)
        elif source_direction == DIRECTION_LEFT:
            self.interactive_children[-1].acceptFocus(source_direction=source_direction, position_hint=position_hint)

    def connectChildren(self):
        #TODO: ensure respect of focus keys
        for child in self.interactive_children:
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_UP, self.shiftFocusUp)
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_DOWN, self.shiftFocusDown)
        for child, child_two in zip(self.interactive_children, self.interactive_children[1:]):
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_RIGHT, child_two.acceptFocus)
            addQueryListener(child_two.id + EVENT_INTERFACE_FOCUS_SHIFT_LEFT, child.acceptFocus)
        for child in self.interactive_children[0:1]:
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_LEFT, self.shiftFocusLeft)
        for child in self.interactive_children[-1:]:
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_RIGHT, self.shiftFocusRight)

class VerticalContainer(InterfaceElement):

    spacing = 0

    @property
    def interactive(self):
        return self.interactive_children

    def _childPosition(self, child_id):
        index = list(self._children.keys()).index(child_id)
        offset = sum([child.height + self.spacing for child in list(self.children)[:index]])
        return self._position + (0, offset)

    def _calculateHeight(self):
        return max(0, sum([child.height + self.spacing for child in self.children]) - self.spacing)

    def connectChildren(self):
        for child in self.interactive_children:
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_LEFT, self.shiftFocusLeft)
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_RIGHT, self.shiftFocusRight)
        for child, child_two in zip(self.interactive_children, self.interactive_children[1:]):
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_UP, child_two.acceptFocus)
            addQueryListener(child_two.id + EVENT_INTERFACE_FOCUS_SHIFT_DOWN, child.acceptFocus)
        for child in self.interactive_children[0:1]:
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_DOWN, self.shiftFocusDown)
        for child in self.interactive_children[-1:]:
            addQueryListener(child.id + EVENT_INTERFACE_FOCUS_SHIFT_UP, self.shiftFocusUp)

class GridContainer(InterfaceElement):

    spacing = (0, 0)

    @property
    def grid_size(self):
        try:
            return self._grid_size
        except AttributeError:
            self._grid_size = (dmax([child.width for child in self.children]),
                               dmax([child.height for child in self.children]))
        return self._grid_size

    def _childPosition(self, child_id):
        location = self._child_locations[child_id]
        if not location:
            return self._position
        x = (self.grid_size[0] + self.spacing[0]) * location[0]
        y = (self.grid_size[1] + self.spacing[1]) * location[1]
        return self._position + (x, y)

    def _calculateHeight(self):
        index = dmax([location[1] for location in self._child_locations.values()])
        return self.grid_size[1] + (index * (self.grid_size[1] + self.spacing[1]))

    def _calculateWidth(self):
        index = dmax([location[0] for location in self._child_locations.values()])
        return self.grid_size[0] + (index * (self.grid_size[0] + self.spacing[0]))

class SpriteElement(InterfaceElement):

    def __init__(self, sprite_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sprite_path = sprite_path
        self._sprite = createGraphic(sprite_path) #TODO: automatically set layer, etc

    @property
    def height(self):
        return self._sprite.height

    @property
    def width(self):
        return self._sprite.width

    def _applyPosition(self):
        self._sprite.pos = self.position

    def changeSprite(self, new_path):
        self._sprite.destroy()
        self._sprite = createGraphic(new_path)
        self._applyPosition()
