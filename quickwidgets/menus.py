# -*- coding: utf-8 -*-

import operator

from kaiengine.gconfig import FULL_MISC_PATH

from kaiengine.display import getWindowDimensionsScaled
from kaiengine.interface import ScreenElement

from .containers import VerticalContainer, HorizontalContainer, GridContainer
from .buttons import Button


class MenuTemplate(ScreenElement):
    
    #not to be used without a container 
    
    button_type = Button
    default_graphic = tuple(FULL_MISC_PATH + ["menugraphics", "menu0.bordered"])
    
    def __init__(self, sprite_path = None, button_type = None, **kwargs):
        if sprite_path is None:
            sprite_path = self.default_graphic
        super().__init__(sprite_path, **kwargs)
        if button_type is not None:
            self.button_type = button_type
        self._first_button = True
        self._buttons = set()
        
        #defaults
        self.border = (8,8)
        self.setSpriteCenter(True, True)
        self.setSpriteFollowCamera(True)
        self.setPos(*map(operator.truediv, getWindowDimensionsScaled(), (2,2)))
        
    def addButton(self, *args, **kwargs):
        ID = self.addChild(self.button_type(*args, **kwargs))
        if self._first_button:
            self.setFocus(ID)
            self._first_button = False
        self._buttons.add(ID)
        return ID
    
    def getAllButtons(self):
        return [self.getChild(ID) for ID in self._buttons]
    
    #overwritten stuff
    
    def removeChild(self, *args, **kwargs):
        ID = super().removeChild(*args, **kwargs)
        self._buttons.discard(ID)
        return ID
    
    def removeAllChildren(self, *args, **kwargs):
        super().removeAllChildren(*args, **kwargs)
        self._buttons.clear()
    
    def getAnchorPoint(self): 
        #return bottom left corner
        extents = self.getExtents()
        return extents[0], extents[2]
    
    def setSpriteCenter(self, *args, **kwargs):
        super().setSpriteCenter(*args, **kwargs)
        self._applyChildrenPositions()
        
    def updateContainerPositions(self, *args, **kwargs):
        maxwidth = 0
        maxheight = 0
        for button in self.getAllButtons():
            try:
                button.updateContainerPositions
            except:
                pass
            else:
                button.updateContainerPositions()
            maxwidth = max(maxwidth, button.getWidth())
            maxheight = max(maxheight, button.getHeight())
        for button in self.getAllButtons():
            button.setDimensions(maxwidth, maxheight)
        super().updateContainerPositions(*args, **kwargs)
    
    
class VerticalMenu(MenuTemplate, VerticalContainer):
    pass

class HorizontalMenu(MenuTemplate, HorizontalContainer):
    pass

class GridMenu(MenuTemplate, GridContainer):
    pass