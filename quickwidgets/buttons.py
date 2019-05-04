# -*- coding: utf-8 -*-

import operator

from kaiengine.gconfig import FULL_MISC_PATH
from kaiengine.interface import ScreenElement

from .containers import Container
from .labels import LabelElement


class Button(Container):
    
    default_graphic = tuple(FULL_MISC_PATH + ["menugraphics", "brown_button.bordered"])
    default_pressed_graphic = tuple(FULL_MISC_PATH + ["menugraphics", "brown_button_pressed.bordered"])
    default_highlight_graphic = tuple(FULL_MISC_PATH + ["menugraphics", "hover.png"])
    default_width = 80
    default_height = 24
    
    def __init__(self, text = None, font = None, font_size = None, sprite_path = None, width = None, height = None, *args, **kwargs):
        super().__init__(sprite_path, **kwargs)
        
        #defaults
        self.border = (4,4)
        
        self._highlight_id = self.addChild(ScreenElement(self.default_highlight_graphic))
        highlight = self.getHighlight()
        highlight.setSpriteShow(False)
        highlight.setSpriteCenter(True,True)
        highlight.setSpriteFollowCamera(True)
        self._label_id = self.addChild(LabelElement(text, font, font_size))
        label = self.getLabel()
        label.setSpriteCenter(True, True)
        label.setSpriteFollowCamera(True)
        if sprite_path is None:
            self.setSprite(self.default_graphic)
        if width is None:
            self.setWidth(self.default_width)
        if height is None:
            self.setHeight(self.default_height)
        
        self.setSpriteFollowCamera(True)
        
    def getLabel(self):
        return self.getChild(self._label_id)
    
    def getHighlight(self):
        return self.getChild(self._highlight_id)
    
    def addHighlight(self):
        self.getHighlight().setSpriteShow(True)
    
    def removeHighlight(self):
        self.getHighlight().setSpriteShow(False)
    
    def setPressedDown(self):
        self.setSprite(self.default_pressed_graphic)
        
    def setUnpressed(self):
        self.setSprite(self.default_graphic)
        
    def _updateHighlight(self):
        self.getHighlight().setDimensions(*self.getDimensions())
        
    #event stuff
    
    def mouseenter(self):
        self.setSelfFocused()
        
    def mouseover(self, *args, **kwargs):
        if not self.isFocused():
            self.setSelfFocused()
        
    def mouseleave(self):
        self.setUnpressed()
    
    def confirmhold(self):
        self.setPressedDown()
        
    def confirm(self):
        self.setUnpressed()
        
    def gainfocus(self):
        self.addHighlight()
        
    def losefocus(self):
        self.setUnpressed()
        self.removeHighlight()
    
    #text stuff
    
    def setText(self, *args, **kwargs):
        self.getLabel().setText(*args, **kwargs)
        parent = self.getParent()
        if parent:
            parent.delayUpdatePositions()
        
    def setFont(self, *args, **kwargs):
        self.getLabel().setFont(*args, **kwargs)
        parent = self.getParent()
        if parent:
            parent.delayUpdatePositions()
        
    #overwritten stuff
    
    def updateContainerPositions(self):
        super().updateContainerPositions()
        label = self.getLabel()
        self.setDimensions(*map(max, self.getDimensions(), map(operator.add, label.getDimensions(), map(operator.mul, self.getBorder(), (2,2)))))
        self._updateHighlight()
    
    def getAnchorPoint(self):
        extents = self.getExtents() #set to middle of button
        return (extents[0] + extents[1])/2, (extents[2] + extents[3])/2
    
    def setSpriteCenter(self, *args, **kwargs):
        super().setSpriteCenter(*args, **kwargs)
        self._applyChildrenPositions()
        
    def _applyChildrenPositions(self):
        super()._applyChildrenPositions()
        self._updateHighlight()
        
    def setWidth(self, *args, **kwargs):
        super().setWidth(*args, **kwargs)
        self._updateHighlight()
        
    def setHeight(self, *args, **kwargs):
        super().setHeight(*args, **kwargs)
        self._updateHighlight()
        