from .interfaceElement import InterfaceElement

from kaiengine.display import createGraphic
from kaiengine.safeminmax import dmax

class HorizontalContainer(InterfaceElement):

    spacing = 0

    def _childPosition(self, child_id):
        index = list(self._children.keys()).index(child_id)
        offset = sum([child.width + self.spacing for child in self._children[:index]])
        return self._position + (offset, 0)

    def _calculateWidth(self):
        return sum([child.width + self.spacing for child in self._children])

class VerticalContainer(InterfaceElement):

    spacing = 0

    def _childPosition(self, child_id):
        index = list(self._children.keys()).index(child_id)
        offset = sum([child.height + self.spacing for child in self._children[:index]])
        return self._position + (0, offset)

    def _calculateHeight(self):
        return sum([child.height + self.spacing for child in self._children])

class GridContainer(InterfaceElement):

    spacing = (0, 0)

    #NOTE: implement event-based system for _grid_size caching/clearing (so child element size changes, etc. can be accommodated)

    @property
    def grid_size(self):
        try:
            return self._grid_size
        except AttributeError:
            self._grid_size = (dmax([child.width for child in self.children]),
                               dmax([child.height for child in self.children]))
        return self._grid_size

    def _childPosition(self, child_id):
        raise NotImplementedError

    def _calculateHeight(self):
        raise NotImplementedError

    def _calculateWidth(self):
        raise NotImplementedError

class SpriteElement(InterfaceElement):

    def __init__(self, sprite_path=None, *args, **kwargs):
        self._sprite_path = sprite_path
        self._sprite = createGraphic(sprite_path) #TODO: automatically setting layer, etc
        self.height = self._sprite.height
        self.width = self._sprite.width

    def _applyPosition(self):
        self._sprite.pos = self._position
