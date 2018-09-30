

from . import settings
from . import display
from .timer import scheduleRealtime, unscheduleRealtime
from .event import addCustomListener, removeCustomListener
from .gconfig import *

fpssprite = None
fpscount = 0

def initializeSimpleFPSCounter():
    global fpssprite, fpstimer
    fpssprite = display.createLabel("FPS: 0", font_size = settings.getValue(DYNAMIC_SETTINGS_FPS_SIZE), color = COLOR_WHITE, layer = DEFAULT_FPS_LAYER)
    fpssprite.follow_camera = True
    scheduleRealtime(simpleFPSUpdate, 1.0, True)
    if settings.getValue(DYNAMIC_SETTINGS_FPS_ON):
        fpssprite.show = True
    else:
        fpssprite.show = False
    addCustomListener(EVENT_TOGGLE_FPS, toggleFPS)

def incrementFPSCount():
    global fpscount
    fpscount += 1

def simpleFPSUpdate(dt):
    global fpscount
    fpssprite.setText( "FPS: " + str(int(float(fpscount) / dt)))
    fpscount = 0

def toggleFPS():
    fpssprite.show = not fpssprite.show

def removeFPS():
    global fpssprite
    if fpssprite:
        fpssprite.destroy()
    fpssprite = None
    unscheduleRealtime(simpleFPSUpdate)
    removeCustomListener(EVENT_TOGGLE_FPS, toggleFPS)
