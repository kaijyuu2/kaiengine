from collections import defaultdict
from itertools import zip_longest

from kaiengine.safeminmax import dmax

class ScreenCoordinates(list):

    def __add__(self, other):
        return ScreenCoordinates([a+b for a, b in zip_longest(self, other, fillvalue=0)])

    def __sub__(self, other):
        return ScreenCoordinates([a-b for a, b in zip_longest(self, other, fillvalue=0)])

class ScreenElement(object):

    _position = ScreenCoordinates((0, 0))
    _display_offset = ScreenCoordinates((0, 0))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = {}

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

    def addChild(self, child_element, *args, **kwargs):
        self._children[child_element.id] = child_element
        return child_element
