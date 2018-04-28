

from . import scheduler
from .framecounter import global_frame_counter
from .timer import gametimer
from .realtimecounter import time_since_last_frame

def tickFrameCounter():
    #must be run once a frame to work
    return global_frame_counter.tickCounter()

def checkCurrentFrame():
    return global_frame_counter.checkCurrentFrame()

def pauseGlobalFrameTimer():
    global_frame_counter.pauseCounter()

def unpauseGlobalFrameTimer():
    global_frame_counter.unpauseCounter()

def checkGlobalFrameTimerPaused():
    global_frame_counter.checkPaused()

def pauseMainGameTimer():
    gametimer.pauseTimer()

def unpauseMainGameTimer():
    gametimer.unpauseTimer()

def getRealtimeSinceLastFrame():
    return time_since_last_frame

def checkSchedule():
    scheduler._checkSchedule(checkCurrentFrame())
    tickFrameCounter()

def updateTimeSinceLastFrame(dt):
    global time_since_last_frame
    time_since_last_frame = dt


#scheduling

def schedule(listener, time, repeat = False, *args, **kwargs):
    '''register a timed event that will happen in time frames.'''
    return scheduler._schedule(listener, time, repeat, *args, **kwargs)

def scheduleRealtime(listener, time, repeat = False, *args, **kwargs):
    '''register a timed event that will happen in time seconds.'''
    return scheduler._scheduleRealtime(listener, time, repeat, *args, **kwargs)

def unschedule(listener):
    scheduler._unschedule(listener)

def unscheduleRealtime(listener):
    scheduler._unscheduleRealtime(listener)

def pauseScheduledListener(listener):
    scheduler._pauseScheduledListener(listener)

def unpauseScheduledListener(listener):
    scheduler._unpauseScheduledListener(listener)

def pauseRealtimeListener(listener):
    scheduler._pauseRealtimeListener(listener)

def unpauseRealtimeListener(listener):
    scheduler._unpauseRealtimeListener(listener)

def clearSchedule():
    """clears entire frame based schedule (not realtime)
    warning: do not use for most cases"""
    scheduler._clearSchedule()
