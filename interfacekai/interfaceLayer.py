

from kaiengine.display import getWindowDimensionsScaled
from kaiengine.timer import FrameTimer
from kaiengine.objectinterface import EventInterface, SchedulerInterface
from kaiengine.debug import checkDebugOn, debugMessage
from .interfaceWidget import InterfaceWidget

from kaiengine.gconfig import *

REPEAT_START_TIME = 30
REPEAT_SECOND_TIME = 5

class InterfaceLayer(InterfaceWidget, EventInterface, SchedulerInterface):
    def __init__(self, parent, child, graphical_layer = None, *args, **kwargs):
        super(InterfaceLayer, self).__init__(None, None,*args, **kwargs)

        self.graphical_layer = graphical_layer
        self.parent = parent
        self.child = child
        self._key_held_timers = {}
        self.allow_key_held = True
        self.setWidgetDimensions(*getWindowDimensionsScaled())
        self.allow_input = True
        self.repeat_start_time = REPEAT_START_TIME
        self.repeat_second_time = REPEAT_SECOND_TIME
        self._top_layer = False
        self._layer_deleted = False

        if self.child is None:
            self.flagSelfTop()

    def setAllowInput(self, val):
        self.allow_input = val



    def getLayerDepth(self):
        """return an integer that represents the (current) depth of this layer. 0 is the base layer"""
        if self.parent is not None:
            return self.parent.getLayerDepth() + 1
        else:
            return 0

    #overwritten stuff

    def _getLayerIncrement(self):
        return LAYER_GRAPHICAL_INCREMENT

    def getGraphicalLayerExplicit(self): #overwrites method from InterfaceWidget
        if self.graphical_layer is None:
            try:
                return float(self.parent.getGraphicalLayerExplicit()) + self._getLayerIncrement()*(self.getGraphicalLayer()+1)
            except AttributeError:
                return 0
        return self.graphical_layer

    #response functions

    def flagSelfTop(self):
        self.unflagSelfTop()
        self.addKeyPressListener(self._layerKeyPress)
        self.addKeyReleaseListener(self._layerKeyRelease)
        self.addMousePressListener(self._layerMousePress)
        self.addMouseReleaseListener(self._layerMouseRelease)
        self.addMouseMoveListener(self._layerMouseMove)
        self.addMouseDragListener(self._layerMouseDrag)
        self.addMouseEnterListener(self._layerMouseEnter)
        self.addMouseExitListener(self._layerMouseExit)
        self.addJoybuttonPressListener(self._layerJoybuttonPress)
        self.addJoybuttonReleaseListener(self._layerJoybuttonRelease)
        self._top_layer = True

    def unflagSelfTop(self):
        self.removeKeyPressListener(self._layerKeyPress)
        self.removeKeyReleaseListener(self._layerKeyRelease)
        self.removeMousePressListener(self._layerMousePress)
        self.removeMouseReleaseListener(self._layerMouseRelease)
        self.removeMouseMoveListener(self._layerMouseMove)
        self.removeMouseDragListener(self._layerMouseDrag)
        self.removeMouseEnterListener(self._layerMouseEnter)
        self.removeMouseExitListener(self._layerMouseExit)
        self.removeJoybuttonPressListener(self._layerJoybuttonPress)
        self.removeJoybuttonReleaseListener(self._layerJoybuttonRelease)
        self.removeKeyHeldTimers()
        self._top_layer = False

    def isTopLayer(self):
        return self._top_layer

    def removeKeyHeldTimers(self):
        self._key_held_timers.clear()
        self.unschedule(self._checkKeyHeld)

    def _checkKeyHeld(self):
        if self._top_layer:
            for key, timer in list(self._key_held_timers.items()):
                if timer.checkCountdown():
                    if self._layerRepeat(key) is None:
                        self.removeKeyHeldTimers()
                        break
                    else:
                        timer.countdownStart(self.repeat_second_time)
        else:
            self.removeKeyHeldTimers()

    def _layerRepeat(self, key, counter = 0):
        if self.allow_input:
            counter += 1
            if counter >= 2:
                return None
        if self.child is None:
            self._layerKeyPress2(key, {})
            return True
        return self.child._layerRepeat(key, counter)

    def _layerResponse(self, method1, method2name, *args, **kwargs):
        if not self.allow_input or not method1( *args, **kwargs):
            if self.parent is not None: #if input not allowed, or method1 returned false, check parent
                return getattr(self.parent, method2name)( *args, **kwargs)
            return False #method1 returned false and no parent to call, so return false
        return True #method1 returned true, so we return true here too


    def _printStack(self):
        debugMessage(self)
        if self.parent is not None:
            self.parent._printStack()

    def _layerKeyPress(self, symbol, *args, **kwargs):
        if checkDebugOn():
            import kaiengine.keybinds
            try:
                if self.isTopLayer() and kaiengine.keybinds.keyMatches(DEBUG_BUTTON, symbol):
                    import gc
                    debugMessage("---")
                    self._printStack()
                    """count = {}
                    for obj in gc.get_objects():
                        key = type(obj).__name__
                        try:count[key] += 1
                        except KeyError: count[key] = 1
                    for i, tup in enumerate(sorted(count.items(), key = lambda x: x[1], reverse = True)):
                        if i > 20:
                            break
                        debugMessage(tup[0] + str(tup[1]))"""
            except NotImplementedError:
                pass
        self._layerKeyPress2(symbol, *args, **kwargs)
        if self.allow_key_held:
            self._key_held_timers[symbol] = FrameTimer()
            self._key_held_timers[symbol].countdownStart(self.repeat_start_time)
            self.scheduleUnique(self._checkKeyHeld, 0, True)

    def _layerKeyPress2(self, *args, **kwargs):
        return self._layerResponse(self._respondKeyPress, "_layerKeyPress", *args, **kwargs)

    def _layerKeyRelease(self, symbol, *args, **kwargs):
        returnval = self._layerResponse(self._respondKeyRelease, "_layerKeyRelease", symbol, *args, **kwargs)
        try:
            del self._key_held_timers[symbol]
        except KeyError:
            pass
        if len(self._key_held_timers) <= 0:
            self.unschedule(self._checkKeyHeld)
        return returnval

    def _layerMousePress(self, *args, **kwargs):
        return self._layerResponse(self._respondMousePress, "_layerMousePress", *args, **kwargs)

    def _layerMouseRelease(self, *args, **kwargs):
        return self._layerResponse(self._respondMouseRelease, "_layerMouseRelease", *args, **kwargs)

    def _layerMouseMove(self, *args, **kwargs):
        return self._layerResponse(self._respondMouseMove, "_layerMouseMove", *args, **kwargs)

    def _layerMouseDrag(self, *args, **kwargs):
        return self._layerResponse(self._respondMouseDrag, "_layerMouseDrag", *args, **kwargs)

    def _layerMouseEnter(self, *args, **kwargs):
        return self._layerResponse(self._respondMouseEnter, "_layerMouseEnter", *args, **kwargs)

    def _layerMouseExit(self, *args, **kwargs):
        return self._layerResponse(self._respondMouseExit, "_layerMouseExit", *args, **kwargs)

    def _layerJoybuttonPress(self, *args, **kwargs):
        return self._layerResponse(self._respondJoybuttonPress, "_layerJoybuttonPress", *args, **kwargs)

    def _layerJoybuttonRelease(self, *args, **kwargs):
        return self._layerResponse(self._respondJoybuttonRelease, "_layerJoybuttonRelease", *args, **kwargs)


    #layer manipulation

    def addLayer(self, layer_type, *args, **kwargs):
        oldchild = self.child
        self.child = layer_type(self, self.child,  *args, **kwargs)
        if oldchild is None:
            self.unflagSelfTop()
        else:
            oldchild.parent = self.child
        return self.child

    def addTopLayer(self, *args, **kwargs):
        if self.child is not None:
            return self.child.addTopLayer(*args, **kwargs)
        else:
            return self.addLayer(*args, **kwargs)

    def deleteLayer(self):
        self._deleteLayer()
        self.destroy()

    def _deleteLayer(self):
        if not self._layer_deleted:
            self._layer_deleted = True
            if self.parent is not None:
                self.parent.child = self.child
                if self.child is None:
                    self.parent.flagSelfTop()
                    self.unflagSelfTop()
                else:
                    self.child.parent = self.parent
                self.parent = None
                self.child = None
                self.removeKeyHeldTimers()
                self.setAllowInput(False)
            else:
                raise Exception("Cannot delete base layer!")

    def deleteHigherLayers(self):
        if self.child is not None:
            self.child._deleteHigherLayers()

    def _deleteHigherLayers(self):
        self.deleteHigherLayers()
        self.deleteLayer()

    def destroy(self):
        try:
            self._deleteLayer()
        except Exception:
            pass
        super(InterfaceLayer, self).destroy()
