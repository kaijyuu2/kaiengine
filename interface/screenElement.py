from collections import defaultdict
from itertools import zip_longest

from kaiengine.event import MOUSE_PARTITION_SIZE_X, MOUSE_PARTITION_SIZE_Y, EVENT_MOUSE_MOVE_SECTION
from kaiengine.safeminmax import dmax
from kaiengine.objectinterface import PositionInterface
from kaiengine.coordinate import Coordinate

def getRelevantMousePartitions(x_min, y_min, x_max, y_max):
    x_values = [x for x in range(x_min//MOUSE_PARTITION_SIZE_X, (x_max//MOUSE_PARTITION_SIZE_X)+1)]
    y_values = [y for y in range(y_min//MOUSE_PARTITION_SIZE_Y, (y_max//MOUSE_PARTITION_SIZE_Y)+1)]
    relevant_keys = [EVENT_MOUSE_MOVE_SECTION[(x, y)] for x in x_values for y in y_values]
    return relevant_keys


class ScreenElement(PositionInterface):

    _display_offset = Coordinate((0, 0))
    _layer_thickness = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._children = {}
        self._child_locations = {}
        self.layer = 0

    def setLayer(self, layer):
        self.layer = layer

    @property
    def layer_thickness(self):
        if self._layer_thickness is not None:
            return self._layer_thickness
        children_thickness = dmax([child.layer_thickness for child in self.children], default=None)
        if children_thickness is not None:
            return children_thickness + 1
        return 1

    @property
    def position(self):
        '''alias for pos attribute'''
        return self.pos

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def width(self):
        return self._calculateWidth()

    @property
    def height(self):
        return self._calculateHeight()

    @property
    def children(self):
        return self._children.values()

    @property
    def extents(self):
        return (self.position[0], self.position[1], self.position[0]+self.width, self.position[1]+self.height)

    @property
    def mouse_move_partitions(self):
        return getRelevantMousePartitions(*self.extents)

    def checkPointWithinElement(self, x, y):
        extents = self.extents
        return extents[0] <= x <= extents[2] and extents[1] <= y <= extents[3]

    def _calculateHeight(self):
        return dmax([child.height for child in self.children])

    def _calculateWidth(self):
        return dmax([child.width for child in self.children])

    def _childPosition(self, child_id):
        return self.getPos()

    def setPosition(self, *args, **kwargs):
        '''alias for setPos'''
        self.setPos(*args, **kwargs)

    def setPos(self, *args, **kwargs):
        super().setPos(*args, **kwargs)
        self._applyPosition()
        for child in self.children:
            child.setPos(self._childPosition(child.id))

    def shiftPosition(self, *args, **kwargs):
        '''alias for movePos'''
        self.movePos(*args, **kwargs)

    def movePos(self, *args, **kwargs):
        super().movePos(*args, **kwargs)
        self._applyPosition()
        for child in self.children:
            child.movePos(*args, **kwargs)

    def _applyPosition(self):
        pass

    def addChild(self, child_element, location=None, *args, **kwargs):
        self._children[child_element.id] = child_element
        self._child_locations[child_element.id] = location
        child_element.setLayer(self.layer + 1) #TODO: improve
        return child_element
