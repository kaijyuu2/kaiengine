from collections import defaultdict

from .interfaceManager import InterfaceManager
from .interfaceLayer import InterfaceLayer
from .interfaceWidget import InterfaceWidget, SpacerWidget
from .interfaceConstants import INTERFACE_TIER_BOTTOM, INTERFACE_TIER_DEFAULT, INTERFACE_TIER_HIGH, INTERFACE_TIER_TOP
from .spriteHandler import registerSprite, removeSprite, makeSprite, updateSpriteImage
from .spriteHandler import destroyAllSprites, checkSpriteExists, clearPreloadedSprites
from .spriteHandler import preloadSprite, processSprites, makeUISprite
from kaiengine.event import addCustomListener, EVENT_REQUEST_LAYER_CREATION
from kaiengine.safeminmax import dmax

manager = InterfaceManager()

_layers = defaultdict(list)

def createLayer(layer_class, tier=INTERFACE_TIER_DEFAULT, **kwargs):
    if tier is None:
        tier = INTERFACE_TIER_DEFAULT
    if _layers[tier]:
        priority = _layers[tier][-1].priority + 1
    else:
        priority = tier
    layer = layer_class(priority=priority, **kwargs)
    _layers[tier].append(layer)

addCustomListener(EVENT_REQUEST_LAYER_CREATION, createLayer)
