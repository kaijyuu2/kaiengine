# -*- coding: utf-8 -*-

from kaiengine.display import getWindowDimensionsScaled
from kaiengine.interface import ScreenElement
from kaiengine.gconfig import WHITE_PIXEL_FILEPATH, COLOR_BLACK

class Scene(ScreenElement):
    '''A very basic top level element.'''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.darkener_id = self.addChild(_Darkener(), False)

        self.setSpriteFollowCamera(True) #set background to follow camera by default
        self.setSpriteDimensions(*getWindowDimensionsScaled()) # tile the background
        self.getSprite().tileTexture()

    #overwritten stuff

    def updateChildrenLayers(self):
        #should return the highest used layer
        lastlayer = super().updateChildrenLayers() + 1
        self.getChild(self.darkener_id).setLayer(lastlayer) #ensure darkener on top
        return lastlayer

class _Darkener(ScreenElement):
    '''child element that darkens the screen. '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fade_total_time = 0
        self.fade_time = 0
        self.done_fading = True
        
        #hardcode the sprite
        self.setSprite(WHITE_PIXEL_FILEPATH)
        self.setSpriteFollowCamera(True)
        self.setSpriteDimensions(*getWindowDimensionsScaled())
        self.setSpriteColor(*COLOR_BLACK)
        self.setSpriteAlpha(0.0)

    def fadeIn(self, time):
        self._fadeStart(time)
        self.setSpriteAlpha(1.0)
        self.schedule(self._fadeIn, 0, True)

    def fadeOut(self, time):
        self._fadeStart(time)
        self.setSpriteAlpha(0.0)
        self.schedule(self._fadeOut, 0, True)

    def checkDoneFading(self):
        return self.done_fading

    def _fadeStart(self, time):
        self.unschedule(self._fadeIn)
        self.unschedule(self._fadeOut)
        time = max(0.0, float(time))
        self.fade_total_time = time
        self.fade_time = time
        self.done_fading = False

    def _fadeIn(self):
        self.fade_time -= 1
        self.setSpriteAlpha(round(max(0.0, self.fade_time) * 16 / self.fade_total_time) / 16)
        if self.fade_time <= 0:
            self.done_fading = True
            self.unschedule(self._fadeIn)

    def _fadeOut(self):
        self.fade_time -= 1
        self.setSpriteAlpha(1.0 - round(max(0.0, self.fade_time) * 16 / self.fade_total_time) / 16)
        if self.fade_time <= 0:
            self.done_fading = True
            self.unschedule(self._fadeOut)
        