

from kaiengine.uidgen import isID

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
    if not isID(listener):
        return scheduler._unschedule(listener)
    else:
        return unscheduleWithID(listener)

def unscheduleWithID(*args, **kwargs):
    return scheduler._unscheduleWithID(*args, **kwargs)

def unscheduleRealtime(*args, **kwargs):
    return scheduler._unscheduleRealtime(*args, **kwargs)

def unscheduleRealtimeWithID(*args, **kwargs):
    return scheduler._unscheduleRealtimeWithID(*args, **kwargs)

def pauseScheduledListener(listener, *args, **kwargs):
    if not isID(listener):
        scheduler._pauseScheduledListener(*args, **kwargs)
    else:
        pauseScheduledListenerWithID(listener, *args, **kwargs)
    
def pauseScheduledListenerWithID(*args, **kwargs):
    scheduler._pauseScheduledListenerWithID(*args, **kwargs)

def unpauseScheduledListener(listener, *args, **kwargs):
    if not isID(listener):
        scheduler._unpauseScheduledListener(*args, **kwargs)
    else:
        unpauseScheduledListenerWithID(listener, *args, **kwargs)

def unpauseScheduledListenerWithID(*args, **kwargs):
    scheduler._unpauseScheduledListenerWithID(*args, **kwargs)

def pauseRealtimeListener(*args, **kwargs):
    scheduler._pauseRealtimeListener(*args, **kwargs)
    
def pauseRealtimeListenerWithID(*args, **kwargs):
    scheduler._pauseRealtimeListenerWithID(*args, **kwargs)

def unpauseRealtimeListener(*args, **kwargs):
    scheduler._unpauseRealtimeListener(*args, **kwargs)
    
def unpauseRealtimeListenerWithID(*args, **kwargs):
    scheduler._unpauseRealtimeListenerWithID(*args, **kwargs)
    

def clearSchedule():
    """clears entire frame based schedule (not realtime)
    warning: do not use for most cases"""
    scheduler._clearSchedule()
