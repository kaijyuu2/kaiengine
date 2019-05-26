# -*- coding: utf-8 -*-

import operator

from kaiengine.gconfig import FULL_MISC_PATH
from kaiengine.interface import ScreenElement
from kaiengine.utilityFuncs import dictUnion

from .containers import Container
from .labels import LabelElement
from .stylesheetkeys import DEFAULT_GRAPHIC, DEFAULT_PRESSED_GRAPHIC, DEFAULT_HIGHLIGHT_GRAPHIC, DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_BORDER 
from .stylesheetkeys import DEFAULT_BUTTON_GRAPHIC, DEFAULT_BUTTON_HEIGHT, DEFAULT_BUTTON_WIDTH, DEFAULT_BUTTON_BORDER

class BaseButton(Container):
    
    stylesheet = dictUnion(Container.stylesheet, {})
    
    def __init__(self, sprite_path = None, width = None, height = None, *args, **kwargs):
        super().__init__(sprite_path, **kwargs)
        
        #defaults
        
        self._highlight_id = self.addChild(ScreenElement(self.stylesheet.get(DEFAULT_HIGHLIGHT_GRAPHIC, tuple(FULL_MISC_PATH + ["menugraphics", "hover.png"])), stylesheet=self.stylesheet))
        highlight = self.getHighlight()
        highlight.setSpriteShow(False)
        highlight.setSpriteCenter(True,True)
        highlight.setSpriteFollowCamera(True)
        self._central_widget_id = None
        sprite_path = sprite_path or self.getOrderedStylesheetData(DEFAULT_BUTTON_GRAPHIC, DEFAULT_GRAPHIC, default=tuple(FULL_MISC_PATH + ["menugraphics", "brown_button.bordered"]))
        if sprite_path is not None:
            self.setSprite(sprite_path)
        width = width or self.getOrderedStylesheetData(DEFAULT_BUTTON_WIDTH, DEFAULT_WIDTH, default=80)
        if width is not None:
            self.setWidth(width)
        height = height or self.getOrderedStylesheetData(DEFAULT_BUTTON_HEIGHT, DEFAULT_HEIGHT, default=24)
        if height is not None:
            self.setHeight(height)
        self.setBorder(*self.getOrderedStylesheetData(DEFAULT_BUTTON_BORDER, DEFAULT_BORDER, default=(4,4)))
        
        self.unpressed_graphic = sprite_path
        self.pressed_graphic = self.stylesheet.get(DEFAULT_PRESSED_GRAPHIC, tuple(FULL_MISC_PATH + ["menugraphics", "brown_button_pressed.bordered"]))
        
        self.setSpriteFollowCamera(True)
        
    def getHighlight(self):
        try:
            return self.getChild(self._highlight_id)
        except AttributeError: #not fully initialized yet
            return None
    
    def addHighlight(self):
        highlight = self.getHighlight()
        if highlight:
            highlight.setSpriteShow(True)
    
    def removeHighlight(self):
        highlight = self.getHighlight()
        if highlight:
            highlight.setSpriteShow(False)
    
    def setPressedDown(self):
        if self.pressed_graphic:
            self.setSprite(self.pressed_graphic)
        
    def setUnpressed(self):
        if self.pressed_graphic and self.unpressed_graphic:
            self.setSprite(self.unpressed_graphic)
        
    def _updateHighlight(self):
        highlight = self.getHighlight()
        if highlight:
            highlight.setDimensions(*self.getDimensions())
        
    def setCentralWidget(self, widget):
        self._central_widget_id = self.addChild(widget)
        cw = self.getCentralWidget()
        cw.setSpriteCenter(True, True)
        cw.setSpriteFollowCamera(True)
        return self._central_widget_id
        
    def getCentralWidget(self):
        try:
            return self.getChild(self._central_widget_id)
        except KeyError:
            return None
        
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
        
    #overwritten stuff
    
    def _updateContainerPositions(self):
        super()._updateContainerPositions()
        central_widget = self.getCentralWidget()
        if central_widget:
            self.setDimensions(*map(max, self.getDimensions(), map(operator.add, central_widget.getDimensions(), map(operator.mul, self.getBorder(), (2,2)))))
        self._updateHighlight()
    
    def getAnchorPoint(self):
        extents = self.getExtents() #set to middle of button
        return (extents[0] + extents[1])/2, (extents[2] + extents[3])/2
    
    def setSpriteCenter(self, *args, **kwargs):
        super().setSpriteCenter(*args, **kwargs)
        self._applyChildrenPositions()
        self.tellParentToUpdate()
        
    def _applyChildrenPositions(self):
        super()._applyChildrenPositions()
        self._updateHighlight()
        self.tellParentToUpdate()
        
    def setWidth(self, *args, **kwargs):
        super().setWidth(*args, **kwargs)
        self._updateHighlight()
        self.tellParentToUpdate()
        
    def setHeight(self, *args, **kwargs):
        super().setHeight(*args, **kwargs)
        self._updateHighlight()
        self.tellParentToUpdate()
        

class LabelButton(BaseButton):
    def __init__(self, text = None, font = None, font_size = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setCentralWidget(LabelElement(text, font, font_size))
        
    #add alias for convenience/being explicit
    getLabel = BaseButton.getCentralWidget
    
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
            
            
class GraphicButton(BaseButton):
    
    
    stylesheet = dictUnion(BaseButton.stylesheet, {DEFAULT_GRAPHIC: None, #default to none
                                                  DEFAULT_PRESSED_GRAPHIC: None})
    
    def __init__(self, *args, central_graphic = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pressed_graphic = None #overwrite these
        self.unpressed_graphic = None #overwrite these
        
        self.setCentralWidget(ScreenElement(stylesheet=self.stylesheet))
        if central_graphic:
            self.setButtonGraphic(central_graphic)
            
    def setButtonGraphic(self, val):
        cw = self.getCentralWidget()
        if cw:
            cw.setSprite(val)
            
    #overwritten stuff
            
    def setSprite(self, *args, **kwargs):
        pass #disallow this
    