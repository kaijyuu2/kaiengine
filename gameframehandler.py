

from .camera import runCamera
from .timer import Timer, scheduleRealtime, unscheduleRealtime, checkSchedule, updateTimeSinceLastFrame
from .simplefpscounter import incrementFPSCount
from . import settings
from .display import updateGraphics, getWindow
from .gconfig import *


frametimer = None
lagtime = 0
main_loop = None
framerate = 1/60.0


def initializeGameFrames(func):
    global frametimer, main_loop, framerate



    updateGraphics()

    main_loop = func
    frametimer = Timer()
    framerate = 1.0 / settings.getValue(DYNAMIC_SETTINGS_FRAMES_PER_SECOND)

    scheduleGameFrame()

    resetLag()

def closeGameFrames():
    unscheduleRealtime(gameFrame)


def scheduleGameFrame():
    global lagtime
    frametime = max(framerate, 1.0/settings.getValue(DYNAMIC_SETTINGS_FPS_CLAMP)) #framerate doesn't change; use fps clamp if you want to lower it
    delay = max(frametime, frametimer.Tick() - lagtime) #subtracting lag time since it's negative
    lagtime = max(min(frametime - delay, 0), -settings.getValue(DYNAMIC_SETTINGS_MAX_LAG_TIME)) #max is a sanity check in case of extreme lag
    scheduleRealtime(gameFrame, 2*frametime - delay)

def dispatchInputEvents():
    getWindow().dispatch_events()

def gameFrame(dt):
    #unscheduleRealtime(GameFrame) #stopgap to prevent leak; ideally whole scheduling system should handle better
    updateTimeSinceLastFrame(dt)
    dispatchInputEvents()
    runCamera()
    main_loop(dt)
    checkSchedule()
    updateGraphics()
    incrementFPSCount()
    scheduleGameFrame()

def resetLag():
    global lagtime
    lagtime = 0.0
    if frametimer:
        frametimer.stopTimer() #prevents lag catch-up; all lag until after the next frame will be ignored
