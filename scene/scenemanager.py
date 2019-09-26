# -*- coding: utf-8 -*-

from kaiengine.objectinterface import EventInterface


manager = None

class SceneManager(EventInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scene_stack = []

    def pushScene(self, newscenetype, *args, **kwargs):
        if self.getCurrentScene():
            self.getCurrentScene().sleepScene()
        try:
            newscene = newscenetype(*args, **kwargs)
        except TypeError: #must of passed an already created scene
            newscene = newscenetype
        self.scene_stack.append(newscene)
        self.getCurrentScene().secondaryInit()

    def popScene(self):
        if self.scene_stack:
            self.getCurrentScene().destroy()
            self.scene_stack = self.scene_stack[:-1]
            if self.scene_stack:
                self.getCurrentScene().wakeUpScene()

    def clearSceneStack(self):
        for scene in self.scene_stack:
            scene.destroy()
        self.scene_stack.clear()

    def getCurrentScene(self):
        try:
            return self.scene_stack[-1]
        except IndexError:
            return None

    def destroy(self):
        super().destroy()
        self.clearSceneStack()


def initializeSceneManager():
    global manager
    manager = SceneManager()

def closeSceneManager():
    global manager
    if manager:
        manager.destroy()
    manager = None

def getSceneManager():
    return manager

def pushScene(*args, **kwargs):
    manager.pushScene(*args, **kwargs)

def popScene(*args, **kwargs):
    manager.popScene(*args, **kwargs)

def clearSceneStack():
    manager.clearSceneStack()

def getCurrentScene():
    return manager.getCurrentScene()
