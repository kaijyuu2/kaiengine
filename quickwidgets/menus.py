# -*- coding: utf-8 -*-

import operator

from kaiengine.display import getWindowDimensionsScaled
from kaiengine.interface import ScreenElement

from .containers import VerticalContainer, HorizontalContainer, GridContainer


class BaseMenu(ScreenElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #defaults
        self.setPos(*map(operator.div, getWindowDimensionsScaled(), (2,2)))
        self.setSpriteCenter(True, True)
    
    
    #overwritten stuff
    
    def getAnchorPoint(self): 
        #return bottom left corner
        extents = self.getExtents()
        return extents[0], extents[2]
    
    
class VerticalMenu(BaseMenu, VerticalContainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)