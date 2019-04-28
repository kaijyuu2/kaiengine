# -*- coding: utf-8 -*-

from kaiengine.display import getWindowDimensionsScaled
from kaiengine.interface import ScreenElement, pushTopElement, popTopElement
from kaiengine.gconfig import WHITE_PIXEL_FILEPATH, COLOR_BLACK

class Scene(ScreenElement):
    '''A very basic top level element, with fade ins/outs and convenience functions to switch to different ones.'''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #fade attributes
        self.fade_total_time = 0
        self.fade_time = 0
        self.done_fading = True
        
        #setup background
        self.setSpriteFollowCamera(True) #set background to follow camera by default
        self.setSpriteDimensions(*getWindowDimensionsScaled()) # tile the background
        self.getSprite().tileTexture()
        
        #setup darkener
        self._darkener_id = self.addChild(ScreenElement(WHITE_PIXEL_FILEPATH), False)
        darkener = self.getDarkener()
        darkener.setSpriteFollowCamera(True)
        darkener.setSpriteDimensions(*getWindowDimensionsScaled())
        darkener.setSpriteColor(*COLOR_BLACK)
        darkener.setSpriteAlpha(0.0)
        
        
        
    #darkener functions
    def getDarkener(self):
        #convenience function
        return self.getChild(self._darkener_id)

    def fadeIn(self, time):
        self._fadeStart(time)
        self.getDarkener().setSpriteAlpha(1.0)
        self.schedule(self._fadeIn, 0, True)

    def fadeOut(self, time):
        self._fadeStart(time)
        self.getDarkener().setSpriteAlpha(0.0)
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
        self.getDarkener().setSpriteAlpha(max(0.0, self.fade_time) / self.fade_total_time)
        if self.fade_time <= 0:
            self.done_fading = True
            self.unschedule(self._fadeIn)

    def _fadeOut(self):
        self.fade_time -= 1
        self.getDarkener().setSpriteAlpha(1.0 - max(0.0, self.fade_time) / self.fade_total_time)
        if self.fade_time <= 0:
            self.done_fading = True
            self.unschedule(self._fadeOut)
            
    #scene change functions
    def fadeToScene(self, scene_type, time, popself = False, args = [], kwargs = {}):
        self.fadeOut(time)
        self.waitForCondition(self._fadeToScene, self.checkDoneFading, scene_type, popself, args, kwargs)
        
    def _fadeToScene(self, scene_type, popself, args, kwargs):
        self.sceneTransition(scene_type(*args, **kwargs), popself)
            
    def sceneTransition(self, scene, popself = False):
        if popself:
            popTopElement()
        pushTopElement(scene)
        
        
    #overwritten stuff

    def updateChildrenLayers(self):
        #should return the highest used layer
        lastlayer = super().updateChildrenLayers() + 1
        self.getDarkener().setLayer(lastlayer) #ensure darkener on top
        return lastlayer
    