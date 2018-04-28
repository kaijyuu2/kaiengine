# -*- coding: utf-8 -*-

from kaiengine.destroyinterface import DestroyInterface


manager = None

class SceneManager(DestroyInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.scene_stack = []
        
    def pushScene(self, newscenetype, *args, **kwargs):
        if self.getCurrentScene():
            self.getCurrentScene().sleepScene()
        self.scene_stack.append(newscenetype(*args, **kwargs))
        self.getCurrentScene().secondaryInit()

    def popScene(self):
        if self.scene_stack:
            self.getCurrentScene().destroy()
            self.scene_stack = self.scene_stack[:-1]
            self.getCurrentScene().wakeUpScene()
            
    def clearSceneStack(self):
        for scene in self.scene_stack:
            scene.destroy()
        self.scene_stack = []

    def getCurrentScene(self):
        try:
            return self.scene_stack[-1]
        except IndexError:
            return None
        
        
def initializeSceneManager():
    global manager
    manager = SceneManager()
    
def closeSceneManager():
    global manager
    if manager:
        manager.destroy()
    manager = None