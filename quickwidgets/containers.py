# -*- coding: utf-8 -*-

import operator

from kaiengine.interface import ScreenElement

class Container(ScreenElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = (0,0)
        self.spacing = None
        self.strict_spacing = False
        self._update_positions = False

    def setBorder(self, x = None, y = None):
        if x is None: x = self.border[0]
        if y is None: y = self.border[1]
        self.border = (x,y)
        
    def getBorder(self):
        return self.border
    
    def getSpacing(self):
        return self.spacing
    
    def setStrictSpacing(self, val):
        if val != self.strict_spacing:
            self.strict_spacing = val
            self.updateContainerPositions()
        
    def getStrictSpacing(self):
        return self.strict_spacing
    
    def delayUpdatePositions(self):
        if not self._update_positions:
            self._update_positions = self.delay(self.updateContainerPositions)
            
    def updateContainerPositions(self):
        self._update_positions = False
    
    #template functions
    
    def setSpacing(self, *args, **kwargs):
        pass
    
    def getChildKey(self, *args, **kwargs):
        return None
        
    
    #overwritten stuff
        
    def removeAllChildren(self):
        super().removeAllChildren()
        self.updateContainerPositions()
        
    def setDimensions(self, *args, **kwargs):
        super().setDimensions(*args, **kwargs)
        self._applyChildrenPositions()

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
        
    #overwritten stuff
    
    def getChildKey(self, childid):
        childid = self.getChild(childid).id #in case child reference was passed
        for i, child in enumerate(self._child_pos_list):
            if child.id == childid:
                return i
        raise IndexError("Child ID not found: " + str(childid))
    
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
    
    def updateContainerPositions(self):
        super().updateContainerPositions()
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
    
    def updateContainerPositions(self):
        super().updateContainerPositions()
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
        self.spacing = (0,0)
        
            
    #overwritten stuff
    
    def getChildKey(self, childid):
        childid = self.getChild(childid).id
        return self._child_pos_dict[childid]
    
    def setSpacing(self, x = None, y = None):
        if x is None: x = self.getSpacing()[0]
        if y is None: y = self.getSpacing()[1]
        self.spacing = (x,y)
        
    def updateContainerPositions(self):
        super().updateContainerPositions()
        maxwidth = {}
        maxheight = {}
        totalelements = [0,0]
        for childid, pos in self._child_pos_dict.items():
            totalelements = map(max, totalelements, map(operator.add, pos, (1,1)))
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
        for childid, pos in self._child_pos_dict.items():
            self.getChild(childid).setElementPosition(totalwidth.get(pos[0], 0), totalheight.get(pos[1], 0))
        self.setDimensions(totalmaxwidth + self.getBorder()[0], totalmaxheight + self.getBorder()[1])
            
    
    def addChild(self, child, pos_tuple, *args, **kwargs):
        newchild = super().addChild(child, *args, **kwargs)
        self._child_pos_dict[newchild.id] = tuple(pos_tuple)
        self.delayUpdatePositions()
        return newchild
    
    def removeChild(self, *args, **kwargs):
        childid = super().removeChild(*args, **kwargs)
        self._child_pos_dict.pop(childid, None)
        self.delayUpdatePositions()
        return childid
    
    