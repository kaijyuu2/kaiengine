from collections import defaultdict
from itertools import zip_longest

from kaiengine.event import MOUSE_PARTITION_SIZE_X, MOUSE_PARTITION_SIZE_Y, EVENT_MOUSE_MOVE_SECTION
from kaiengine.safeminmax import dmax

def getRelevantMousePartitions(x_min, y_min, x_max, y_max):
    x_values = [x for x in range(x_min//MOUSE_PARTITION_SIZE_X, (x_max//MOUSE_PARTITION_SIZE_X)+1)]
    y_values = [y for y in range(y_min//MOUSE_PARTITION_SIZE_Y, (y_max//MOUSE_PARTITION_SIZE_Y)+1)]
    relevant_keys = [EVENT_MOUSE_MOVE_SECTION[(x, y)] for x in x_values for y in y_values]
    return relevant_keys

class ScreenCoordinates(list):

    def __add__(self, other):
        return ScreenCoordinates([a+b for a, b in zip_longest(self, other, fillvalue=0)])

    __radd__ = __add__

    def __sub__(self, other):
        return ScreenCoordinates([a-b for a, b in zip_longest(self, other, fillvalue=0)])

    __rsub__ = __sub__

class ScreenElement(object):

    _position = ScreenCoordinates((0, 0))
    _display_offset = ScreenCoordinates((0, 0))

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._children = {}
        self._child_locations = {}

    @property
    def position(self):
        return self._position

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
        return self._position

    def _setPosition(self, position):
        self._position = position + self._display_offset
        self._applyPosition()

    def setPosition(self, position):
        self._setPosition(position)
        for child in self.children:
            child.setPosition(self._childPosition(child.id))

    def _shiftPosition(self, offset):
        self._position = self._position + offset
        self._applyPosition()

    def shiftPosition(self, offset):
        self._shiftPosition(offset)
        for child in self.children:
            child.shiftPosition(offset)

    def _applyPosition(self):
        pass

    def addChild(self, child_element, location=None, *args, **kwargs):
        self._children[child_element.id] = child_element
        self._child_locations[child_element.id] = location
        return child_element
