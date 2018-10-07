from .interfaceElement import InterfaceElement

from kaiengine.display import createGraphic
from kaiengine.safeminmax import dmax

class HorizontalContainer(InterfaceElement):

    #TODO: allow location-based positioning

    spacing = 0

    def _childPosition(self, child_id):
        index = list(self._children.keys()).index(child_id)
        offset = sum([child.width + self.spacing for child in list(self._children.values())[:index]])
        return self._position + (offset, 0)

    def _calculateWidth(self):
        return max(0, sum([child.width + self.spacing for child in self._children.values()]) - self.spacing)

class VerticalContainer(InterfaceElement):

    spacing = 0

    def _childPosition(self, child_id):
        index = list(self._children.keys()).index(child_id)
        offset = sum([child.height + self.spacing for child in list(self._children.values())[:index]])
        return self._position + (0, offset)

    def _calculateHeight(self):
        return max(0, sum([child.height + self.spacing for child in self._children.values()]) - self.spacing)

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
