# -*- coding: utf-8 -*-

import operator

from kaiengine.interface import ScreenElement

class _Container(ScreenElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = (0,0)
        self.spacing = None
        self.strict_spacing = False

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
    
    #template functions
    
    def setSpacing(self, *args, **kwargs):
        pass
        
    def updateContainerPositions(self):
        pass
    
    #overwritten stuff
        
    def removeAllChildren(self):
        super().removeAllChildren()
        self.updateContainerPositions()

class _LinearContainer(_Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._child_pos_list = []
        self.spacing = 0
        
    #overwritten stuff
    
    def setSpacing(self, newval):
        self.spacing = newval
    
    def addChild(self, *args, **kwargs):
        newchild = super().addChild(*args, **kwargs)
        self._child_pos_list.append(newchild.id)
        self.updateContainerPositions()
        return newchild
    
    def removeChild(self, *args, **kwargs):
        childid = super().removeChild(*args, **kwargs)
        try: self._child_pos_list.remove(childid)
        except ValueError: pass
        self.updateContainerPositions()
        return childid
    
class VerticalContainer(_LinearContainer):
    
    #overwritten stuff
    
    def updateContainerPositions(self):
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
        self.setDimensions(maxwidth + self.getBorder()[0] * 2, totalheight + self.getBorder()[1] * 2)
        
class HorizontalContainer(_LinearContainer):
    
    #overwritten stuff
    
    def updateContainerPositions(self):
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
        self.setDimensions(totalwidth + self.getBorder()[0] * 2, maxheight + self.getBorder()[1] * 2)
        
        
class GridContainer(_Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._child_pos_dict = {}
        self.spacing = (0,0)
        
            
    #overwritten stuff
    
    def setSpacing(self, x = None, y = None):
        if x is None: x = self.getSpacing()[0]
        if y is None: y = self.getSpacing()[1]
        self.spacing = (x,y)
        
    def updateContainerPositions(self):
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
            
    
    def addChild(self, pos_tuple, *args, **kwargs):
        newchild = super().addChild(*args, **kwargs)
        self._child_pos_dict[newchild.id] = tuple(pos_tuple)
        return newchild
    
    def removeChild(self, *args, **kwargs):
        childid = super().removeChild(*args, **kwargs)
        self._child_pos_dict.pop(childid, None)
        return childid
    
    