# -*- coding: utf-8 -*-

from kaiengine.sDict import sDict
from kaiengine.baseobject import BaseObject
from kaiengine.objectinterface import GraphicInterface, EventInterface, SchedulerInterface
from kaiengine.darkener import Darkener
from kaiengine.audio import playMusic, stopMusic
from kaiengine.objects import createActor
from kaiengine.debug import debugMessage

from kaiengine.gconfig import *

ACTOR_TYPE = "type"
ACTOR_POS = "pos"
ACTOR_SPRITE = "sprite"

FADE_TIME = 60 #one second

class Scene(BaseObject, GraphicInterface, EventInterface, SchedulerInterface):

    default_prop = {SCENE_BG_FILENAME: None,
                    SCENE_MUSIC_FILENAME: None,
                    SCENE_ACTOR_LIST: []}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.darkener = None

        self.actor_factory = createActor

        self.actors = sDict()

        self.schedule(self.updateActorPriority, 1, True)

    def secondaryInit(self):
        '''secondary initialization after scene has been registered'''
        self.setSpriteShow(True)
        self.darkener = Darkener()
        self.playSceneMusic()
        self.loadActors()

    def updateActorPriority(self):
        '''sort actors by y position and give priority to ones that are lower on the screen'''
        actors = sorted(list(self.actors.values()), key=lambda x: x.getPos()[1], reverse=True) #sort by y pos
        for i, actor in enumerate(actors):
            actor.setSpriteLayer(actor.getBaseLayer() + ACTOR_LAYER_INCREMENT * i)

    def setActorFactory(self, factory):
        self.actor_factory = factory

    def getActorFactory(self, actordata = None): #data passed in case this is overwritten
        return self.actor_factory

    def loadActors(self):
        for actordict in self.actor_list:
            try:
                newactor = self.getActorFactory(actordict)(actordict.pop(ACTOR_TYPE, None), self)
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
        if not self.sleeping:
            self.darkener.fadeOut(time)
            if len(args) + len(kwargs) > 0:
                self.waitForFade(*args, **kwargs)

    def sceneFadeIn(self, time = FADE_TIME, *args, **kwargs):
        if not self.sleeping:
            self.darkener.fadeIn(time)
            if len(args) + len(kwargs) > 0:
                self.waitForFade(*args, **kwargs)

    def checkDoneFading(self):
        return self.darkener.checkDoneFading()

    def waitForFade(self, method, *args, **kwargs):
        if not self.sleeping:
            self.schedule(self._waitForFade, 1, True, method, *args, **kwargs)
            self._waitForFade(method, *args, **kwargs)

    def _waitForFade(self, method, *args, **kwargs):
        if not self.sleeping:
            if self.checkDoneFading():
                self.unschedule(self._waitForFade)
                method(*args, **kwargs)



    def destroy(self):
        super().destroy()
        self.removeAllActors()
