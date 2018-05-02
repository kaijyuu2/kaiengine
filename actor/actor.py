# -*- coding: utf-8 -*-

"""objects that can move around are actors"""

from kaiengine.objectinterface import MovementInterfaceFrames, GraphicInterface, SchedulerInterface

from kaiengine.gconfig import *
import copy

class Actor(GraphicInterface, MovementInterfaceFrames, SchedulerInterface):

    #basic default properties

    vars()[GPATH] = copy.copy(ACTOR_GRAPHICS_FULL_PATH)

    #other default properties

    default_prop = {ACTOR_STARTING_SPRITE: DEFAULT_INVALID_GRAPHIC}


    def __init__(self, filename = None, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self._actor_index = -1
        self.baselayer = DEFAULT_ACTOR_LAYER #for graphical layering; is generally used in scenes to order actor layers
        
        if self.starting_sprite is not None:
            self.setSprite(self.starting_sprite) #set default sprite

    def setBaseLayer(self, layer):
        self.baselayer = layer

    def getBaseLayer(self):
        return self.baselayer 

    def getActorIndex(self):
        return self._actor_index

    #overwritten stuff
    
    def getGraphicPath(self, filepath):
        '''overwrites something from GraphicInterface'''
        if filepath != DEFAULT_INVALID_GRAPHIC:
            return super(Actor, self).getGraphicPath(filepath)
        return self._getGraphicPath(MISC_GRAPHICS_FULL_PATH, filepath)