# -*- coding: utf-8 -*-

from kaiengine.sDict import sDict
from kaiengine.baseobject import BaseObject
from kaiengine.objectinterface import GraphicInterface, EventInterface
from kaiengine.darkener import Darkener
from kaiengine.audio import playMusic, stopMusic


ACTOR_TYPE = "type"
ACTOR_POS = "pos"
ACTOR_SPRITE = "sprite"

FADE_TIME = 60 #one second

class Scene(BaseObject, GraphicInterface, EventInterface):
    
    default_prop = {SCENE_BG_FILENAME: None
                    SCENE_MUSIC_FILENAME: None,
                    SCENE_ACTOR_LIST: []}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.actors = sDict()
        
    def secondaryInit(self):
        '''secondary initialization after scene has been registered'''
        self.setSpriteShow(True)
        self.darkener = Darkener()
        self.playSceneMusic()
        self.loadActors()
        
    def loadActors(self):
        for actordict in self.actor_list:
            try:
                newactor = CreateActor(actordict.pop(ACTOR_TYPE, None), self)
                pos = actordict.pop(ACTOR_POS)
                self.addActor(newactor)
                newactor.setPos(*pos)
                newsprite = actordict.pop(ACTOR_SPRITE, None)
                if newsprite != "" and newsprite != None:
                    newactor.setSprite(newsprite)
                newactor.setExtraData(actordict)
            except Exception as e:
                debugMessage("Failed to create map actor!")
                debugMessage(e)
                debugMessage(actordict)
                
    def addActor(self, actor):
        """Must have already created actor object"""
        self.actors.append(actor)
        lastactor = self.getLastCreatedActor()
        lastactor._actor_index = self.actors.last_key()
        return lastactor

    def getActorByIndex(self, actorindex, suppress_error = False):
        try:
            return self.actors[actorindex]
        except KeyError:
            if not (suppress_error or self.destroyed):
                debugMessage("actor not found in scene when queried by index: " + str(actorindex))
                raise
            return None

    def removeActor(self, actor):
        for key, val in self.actors.items():
            if val == actor:
                if not val.destroyed:
                    val.destroy()
                try:
                    del self.actors[key]
                except KeyError:
                    pass

    def removeActorByIndex(self, actorindex):
        try:
            if not self.actors[actorindex].destroyed:
                self.actors[actorindex].destroy()
            del self.actors[actorindex]
        except KeyError:
            pass

    def removeAllActors(self):
        for actor in self.actors.values():
            actor.destroy()
        self.actors.clear()

    def getLastCreatedActor(self):
        return self.actors.last_item()

    def getActor(self, index):
        try:
            return self.actors[index]
        except KeyError:
            return None

    def getAllActors(self):
        return list(self.actors.values())

        
    def playSceneMusic(self):
        if self.music is not None:
            playMusic(self.music)
            
    def sceneFadeOut(self, time = FADE_TIME, *args, **kwargs):
        if not self.scene_hidden:
            self.darkener.fadeOut(time)
            if len(args) + len(kwargs) > 0:
                self.waitForFade(*args, **kwargs)

    def sceneFadeIn(self, time = FADE_TIME, *args, **kwargs):
        if not self.scene_hidden:
            self.darkener.fadeIn(time)
            if len(args) + len(kwargs) > 0:
                self.waitForFade(*args, **kwargs)

    def checkDoneFading(self):
        return self.darkener.checkDoneFading()

    def waitForFade(self, method, *args, **kwargs):
        if not self.scene_hidden:
            self.schedule(self._waitForFade, 1, True, method, *args, **kwargs)
            self._waitForFade(method, *args, **kwargs)

    def _waitForFade(self, method, *args, **kwargs):
        if not self.scene_hidden:
            if self.checkDoneFading():
                self.unschedule(self._waitForFade)
                method(*args, **kwargs)
            
            
            
    def destroy(self):
        super().destroy()
        self.removeAllActors()