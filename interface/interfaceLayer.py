from kaiengine.gconfig import COLOR_BLACK, WIDGET_PATH
from kaiengine.event import ListenerRegistryMeta, customEvent
from kaiengine.event import addCustomListener, removeCustomListener
from kaiengine.event import EVENT_KEY_PRESS, EVENT_KEY_RELEASE
from kaiengine.event import EVENT_MOUSE_PRESS, EVENT_MOUSE_RELEASE
from kaiengine.event import EVENT_MOUSE_MOVE, EVENT_MOUSE_DRAG
from kaiengine.event import EVENT_JOYPAD_PRESS, EVENT_GAME_CLOSE
from kaiengine.event import EVENT_MOUSE_ENTER, EVENT_MOUSE_EXIT
from kaiengine.event import EVENT_REQUEST_LAYER_CREATION, EVENT_FADE_IN
from kaiengine.event import EVENT_REMOVE_INPUT_LOCKS, EVENT_LOCK_INPUT
from kaiengine.timer import Schedule
from kaiengine.objectdestroyederror import ObjectDestroyedError
from kaiengine.interface.spriteHandler import makeSprite, registerSprite, removeSprite
from kaiengine.interface.interfaceWidget import FadeWidget
from kaiengine.objectinterface import EventInterface, SchedulerInterface
from kaiengine.keybinds import keyMatches, keyMatchesAny
from kaiengine.uidgen import generateUniqueID
from kaiengine import settings
from kaiengine.debug import debugMessage
from sys import modules
from collections import defaultdict
from .interfaceConstants import INTERFACE_TIER_HIGH

class InterfaceLayer(EventInterface, metaclass=ListenerRegistryMeta):

    """Base class for event-response interface layers.

        init parameters:

        priority: determines the order in which layers receive events (usually handled by creation function)
        """

    blocking = False

    def __init__(self, priority=0):
        super().__init__()
        self.priority = priority
        self._ID = generateUniqueID("_INTERFACE_LAYER_")
        self._delete = False
        self._widget = None
        self._fadeLayer = None
        self._custom_listeners = {}
        self._input_locks = set()
        if self.blocking:
            customEvent(EVENT_LOCK_INPUT, self.priority, self._ID)
        self.addCustomListener(EVENT_LOCK_INPUT, self._addInputLock)
        self.addCustomListener(EVENT_REMOVE_INPUT_LOCKS, self._removeInputLock)

    def _addInputLock(self, level, ID):
        if level > self.priority:
            self._input_locks.add(ID)

    def _removeInputLock(self, ID):
        try:
            self._input_locks.remove(ID)
        except KeyError:
            pass

    def _showWidget(self):
        if self._widget:
            self._widget.show()

    def _hideWidget(self):
        if self._widget:
            self._widget.hide()

    def addWidget(self, widget):
        """Registers a widget so it's shown, hidden, and destroyed with the layer."""
        if self._widget:
            self.destroyWidget()
        self._widget = widget

    def destroyWidget(self):
        """Removes the layer's registered widget."""
        if self._widget:
            self._widget.destroy()
        self._widget = None

    def updateWidget(self, *args, **kwargs):
        """Calls the update method of the layer's widget."""
        if self._widget:
            self._widget.update(*args, **kwargs)

    def destroy(self):
        """Destroy the layer and all associated objects, and create next layer if appropriate."""
        customEvent(EVENT_REMOVE_INPUT_LOCKS, self._ID)
        super().destroy()
        self.destroyWidget()
        self._delete = True

    def fade(self, **kwargs):
        """Convenience function for a full-screen fade effect."""
        return self.createLayer(FadeLayer, tier=INTERFACE_TIER_HIGH, **kwargs)

    def fadeIn(self):
        customEvent(EVENT_FADE_IN)

    def createLayer(self, newLayerClass, tier=None, **kwargs):
        """Convenience function to request the creation of a new layer."""
        customEvent(EVENT_REQUEST_LAYER_CREATION, newLayerClass, tier=tier, **kwargs)

    def _initListener(self, event_key, func, priority, lock):
        """Handle instantiation for compatibility with ListenerRegistryMeta."""
        def instantiated(*args, **kwargs):
            if (not lock) or (not self._input_locks):
                return func(self, *args, **kwargs)
        self.addCustomListener(event_key, instantiated, priority)

class FadeLayer(InterfaceLayer, SchedulerInterface):

    """Layer for a full-screen fade effect."""

    blocking = True

    def __init__(self, speed=15, priority=90001, startFadedOut=False, **kwargs):
        super(FadeLayer, self).__init__(priority=priority, **kwargs)
        self.speed = speed
        self.addWidget(FadeWidget(speed=speed, startFaded=startFadedOut))
        if startFadedOut:
            fadeInDelay = 0
        else:
            fadeInDelay = self.speed * 5
        self.Schedule(self.destroy, fadeInDelay + self.speed*4)
