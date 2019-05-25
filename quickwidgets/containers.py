# -*- coding: utf-8 -*-

import operator

from kaiengine.interface import ScreenElement
from kaiengine.safeminmax import dmax
from kaiengine.timer import DelayedEventException
from kaiengine.utilityFuncs import dictUnion

from .stylesheetkeys import DEFAULT_BORDER

class Container(ScreenElement):

    stylesheet = dictUnion(ScreenElement.stylesheet, {DEFAULT_BORDER: (0,0)})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = self.stylesheet.get(DEFAULT_BORDER, (0,0))
        self.spacing = None
        self.strict_spacing = False
        self._update_positions = False
        self._currently_updating = False

    def setBorder(self, x = None, y = None):
        if x is None: x = self.border[0]
        if y is None: y = self.border[1]
        self.border = (x,y)
        self.updateContainerPositions()

    def getBorder(self):
        return self.border

    def getSpacing(self):
        return self.spacing

    def setStrictSpacing(self, val):
        if val != self.strict_spacing:
            self.strict_spacing = val
            self.delayUpdatePositions()

    def getStrictSpacing(self):
        return self.strict_spacing

    def delayUpdatePositions(self):
        if not self._update_positions and not self._currently_updating:
            try:
                self._update_positions = self.delay(self.updateContainerPositions, self.getLayer)
            except DelayedEventException:
                pass

    def updateContainerPositions(self):
        if not self._currently_updating: #prevent infinite loops
            self.undelay(self._update_positions)
            self._update_positions = False
            self._currently_updating = True
            self._updateContainerPositions()
            self._currently_updating = False
        
    def _updateContainerPositions(self):
        pass
        
    def containerPositionsUpdated(self):
        return not bool(self._update_positions)

    #template functions

    def setSpacing(self, *args, **kwargs):
        pass

    def getChildKey(self, *args, **kwargs):
        return None

    def getChildByKey(self, *args, **kwargs):
        return None


    #overwritten stuff

    def getWidth(self):
        if not self.containerPositionsUpdated():
            self.updateContainerPositions()
        return super().getWidth()
    
    def getHeight(self):
        if not self.containerPositionsUpdated():
            self.updateContainerPositions()
        return super().getHeight()
    
    def getExtents(self):
        if not self.containerPositionsUpdated():
            self.updateContainerPositions()
        return super().getExtents()

    def getAnchorPoint(self):
        #return bottom left corner
        extents = self.getExtents()
        return extents[0], extents[2]

    def removeAllChildren(self):
        super().removeAllChildren()
        self.delayUpdatePositions()

    def setDimensions(self, *args, **kwargs):
        super().setDimensions(*args, **kwargs)
        self._applyChildrenPositions()

    def updateElement(self):
        super().updateElement()
        self.delayUpdatePositions()

class _LinearContainer(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._child_pos_list = []
        self.spacing = 0

    def insertChild(self, index, *args, **kwargs):
        newchild = self.addChild(*args, **kwargs)
        newchildid = self._child_pos_list.pop(-1)
        self._child_pos_list.insert(index, newchildid)
        return newchild

    def getLength(self):
        return len(self._child_pos_list)

    #overwritten stuff

    def getChildKey(self, childid):
        childid = self.getChild(childid).id #in case child reference was passed
        for i, otherchildid in enumerate(self._child_pos_list):
            if otherchildid == childid:
                return i
        raise IndexError("Child ID not found: " + str(childid))

    def getChildByKey(self, child_key):
        return self.getChild(self._child_pos_list[child_key])

    def setSpacing(self, newval):
        self.spacing = newval

    def addChild(self, *args, **kwargs):
        newchild = super().addChild(*args, **kwargs)
        self._child_pos_list.append(newchild.id)
        self.delayUpdatePositions()
        return newchild

    def removeChild(self, *args, **kwargs):
        childid = super().removeChild(*args, **kwargs)
        try: self._child_pos_list.remove(childid)
        except ValueError: pass
        self.delayUpdatePositions()
        return childid

class VerticalContainer(_LinearContainer):

    #overwritten stuff


    def _updateContainerPositions(self):
        super()._updateContainerPositions()
        maxwidth = 0
        maxheight = 0
        totalheight = self.getBorder()[1]
        for i, childid in enumerate(reversed(self._child_pos_list)):
            if i != 0:
                totalheight += self.getSpacing()
            child = self.getChild(childid)
            maxwidth = max(maxwidth, child.getWidth())
            maxheight = max(maxheight, child.getHeight())
            child.setElementPosition(self.getBorder()[0], totalheight)
            if not self.getStrictSpacing():
                totalheight += child.getHeight()
        self.setDimensions(maxwidth + self.getBorder()[0] * 2, totalheight + self.getBorder()[1])

class HorizontalContainer(_LinearContainer):

    #overwritten stuff

    def _updateContainerPositions(self):
        super()._updateContainerPositions()
        maxwidth = 0
        maxheight = 0
        totalwidth = self.getBorder()[0]
        for i, childid in enumerate(reversed(self._child_pos_list)):
            if i != 0:
                totalwidth += self.getSpacing()
            child = self.getChild(childid)
            maxwidth = max(maxwidth, child.getWidth())
            maxheight = max(maxheight, child.getHeight())
            child.setElementPosition(totalwidth, self.getBorder()[1])
            if not self.getStrictSpacing():
                totalwidth += child.getWidth()
        self.setDimensions(totalwidth + self.getBorder()[0], maxheight + self.getBorder()[1] * 2)


class GridContainer(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._child_pos_dict = {}
        self._child_id_dict = {}
        self._grid_sizes = [0,0,0,0]
        self.spacing = (0,0)

    def getGridSizes(self):
        return tuple(self._grid_sizes)

    #overwritten stuff

    def getChildKey(self, childid):
        childid = self.getChild(childid).id
        return self._child_id_dict[childid]

    def getChildByKey(self, child_key):
        return self.getChild(self._child_pos_dict[child_key])

    def setSpacing(self, x = None, y = None):
        if x is None: x = self.getSpacing()[0]
        if y is None: y = self.getSpacing()[1]
        self.spacing = (x,y)

    def _updateContainerPositions(self):
        super()._updateContainerPositions()
        maxwidth = {}
        maxheight = {}
        totalelements = [0,0]
        for pos, childid in self._child_pos_dict.items():
            totalelements = list(map(max, totalelements, map(operator.add, pos, (1,1))))
            if not self.getStrictSpacing():
                child = self.getChild(childid)
                maxwidth[pos[0]] = max(maxwidth.get(pos[0], 0), child.getWidth())
                maxheight[pos[1]] = max(maxheight.get(pos[1], 0), child.getHeight())
        totalwidth = {}
        totalheight = {}
        totalmaxwidth = self.getBorder()[0]
        totalmaxheight = self.getBorder()[1]
        for i in range(totalelements[0]):
            spacing = self.getSpacing()[0] if i != 0 else 0
            totalwidth[i] = totalwidth.get(i - 1, self.getBorder()[0]) + maxwidth.get(i - 1, 0) + spacing
            totalmaxwidth += maxwidth.get(i, 0) + spacing
        for i in range(totalelements[1]):
            spacing = self.getSpacing()[1] if i != 0 else 0
            totalheight[i] = totalheight.get(i - 1, self.getBorder()[1]) + maxheight.get(i - 1, 0) + spacing
            totalmaxheight += maxheight.get(i, 0) + spacing
        for pos, childid in self._child_pos_dict.items():
            self.getChild(childid).setElementPosition(totalwidth.get(pos[0], 0), totalheight.get(pos[1], 0))
        self.setDimensions(totalmaxwidth + self.getBorder()[0], totalmaxheight + self.getBorder()[1])


    def addChild(self, pos_tuple, child, *args, **kwargs):
        newchild = super().addChild(child, *args, **kwargs)
        self._child_pos_dict[tuple(pos_tuple)] = newchild.id
        self._child_id_dict[newchild.id] = tuple(pos_tuple)
        self._grid_sizes[0] = min(self._grid_sizes[0], pos_tuple[0])
        self._grid_sizes[1] = max(self._grid_sizes[1], pos_tuple[0])
        self._grid_sizes[2] = min(self._grid_sizes[2], pos_tuple[1])
        self._grid_sizes[3] = max(self._grid_sizes[3], pos_tuple[1])
        self.delayUpdatePositions()
        return newchild

    def removeChild(self, *args, **kwargs):
        childid = super().removeChild(*args, **kwargs)
        pos = self._child_id_dict.pop(childid, None)
        self._child_pos_dict.pop(pos, None)
        self.delayUpdatePositions()
        return childid

