from kaiengine import event
from kaiengine.debug import checkDebugOn

from kaiengine.gconfig import *


# NOTE: Interface Manager will pass-through unhandled errors encountered
#       in input response if and only if DYNAMIC_SETTINGS_DEBUG_ON is True.
#       (That is, errors that a layer raises in response to user input
#        will be ignored in production mode, on the assumption that this
#        is better than breaking the program execution entirely.)

class InterfaceManager(object):

    def __init__(self):
        self.pressedKeys = set()
        self.pressedButtons = set()
        self.interfaceLayers = []
        self.runUpdate = self._runUpdate

        event.addKeyPressListener(self.keyPressed, 1)
        event.addKeyReleaseListener(self.keyReleased, 1)
        event.addMousePressListener(self.mousePressed, 1)
        event.addMouseReleaseListener(self.mouseReleased, 1)
        event.addMouseMoveListener(self.mouseMoved, 1)
        event.addMouseDragListener(self.mouseDragged, 1)
        event.addMouseEnterListener(self.mouseEntered, 1)
        event.addMouseExitListener(self.mouseExited, 1)
        event.addJoybuttonPressListener(self.joybuttonPressed, 1)

    def framesMode(self):
        '''Stop providing frame delta to layers.'''
        self.runUpdate = self._runUpdateFrames

    def addInterfaceLayer(self, layer, top=False):
        '''Add a new interface layer and sort by priority.'''
        layer.top = top
        self.interfaceLayers.append(layer)
        self.interfaceLayers.sort(key=lambda item: item.priority, reverse=True) #higher priority = earlier in list
        self.interfaceLayers.sort(key=lambda item: item.top, reverse=True)

    def respondKeyPress(self, symbol, modifiers):
        try:
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondKeyPress(symbol, modifiers):
                        return
        except:
            if checkDebugOn():
                raise

    def respondKeyHold(self, symbol):
        try:
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondKeyHold(symbol):
                        return
        except:
            if checkDebugOn():
                raise

    def keyPressed(self, symbol, modifiers):
        self.pressedKeys.add(symbol)
        self.respondKeyPress(symbol, modifiers)

    def respondJoybuttonPress(self, joystick, button):
        try:
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondJoybuttonPress(joystick, button):
                        return
        except:
            if checkDebugOn():
                raise

    def joybuttonPressed(self, joystick, button):
        self.respondJoybuttonPress(joystick, button)

    def keyReleased(self, symbol, modifiers):
        try:
            try:
                self.pressedKeys.remove(symbol)
            except KeyError:
                pass
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondKeyRelease(symbol, modifiers):
                        return
        except:
            if checkDebugOn():
                raise

    def mousePressed(self, x, y, button, modifiers):
        try:
            self.pressedButtons.add(button)
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondMousePress(x, y, button, modifiers):
                        return
        except:
            if checkDebugOn():
                raise

    def mouseReleased(self, x, y, button, modifiers):
        try:
            try:
                self.pressedButtons.remove(button)
            except KeyError:
                pass
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondMouseRelease(x, y, button, modifiers):
                        return
        except:
            if checkDebugOn():
                raise

    def mouseMoved(self, x, y, dx, dy):
        try:
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondMouseMove(x, y, dx, dy):
                        return
        except:
            if checkDebugOn():
                raise

    def mouseDragged(self, x, y, dx, dy, button, modifiers):
        try:
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondMouseDrag(x, y, dx, dy, button, modifiers):
                        return
        except:
            if checkDebugOn():
                raise

    def mouseEntered(self, x, y):
        try:
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondMouseEnter(x, y):
                        return
        except:
            if checkDebugOn():
                raise

    def mouseExited(self, x, y):
        try:
            for layer in self.interfaceLayers[:]:
                if not layer._delete:
                    if layer.respondMouseExit(x, y):
                        return
        except:
            if checkDebugOn():
                raise

    def _runUpdate(self, dt):
        for symbol in self.pressedKeys:
            self.respondKeyHold(symbol)
        toDelete = []
        for i, layer in enumerate(self.interfaceLayers):
            if layer._delete:
                toDelete.append(i)
        for i in reversed(toDelete):
            self.interfaceLayers.pop(i)
        for layer in self.interfaceLayers[:]:
            if layer.processTick(dt): break
        toDelete = []
        for i, layer in enumerate(self.interfaceLayers):
            if layer._delete:
                toDelete.append(i)
        for i in reversed(toDelete):
            self.interfaceLayers.pop(i)

    def _runUpdateFrames(self):
        for symbol in self.pressedKeys:
            self.respondKeyHold(symbol)
        toDelete = []
        for i, layer in enumerate(self.interfaceLayers):
            if layer._delete:
                toDelete.append(i)
        for i in reversed(toDelete):
            self.interfaceLayers.pop(i)
        for layer in self.interfaceLayers[:]:
            if layer.processTick(): break
        toDelete = []
        for i, layer in enumerate(self.interfaceLayers):
            if layer._delete:
                toDelete.append(i)
        for i in reversed(toDelete):
            self.interfaceLayers.pop(i)

    def initializeBaseLayer(self, layerClass, **kwargs):
        self.addInterfaceLayer(layerClass(priority=0, **kwargs))
