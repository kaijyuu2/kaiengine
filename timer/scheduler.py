
#functions/etc for scheduling logic

from .timer import Timer
from .maingamescheduler import getGameScheduler

from kaiengine.sDict import sDict
from kaiengine.uidgen import generateUniqueID

import functools
import traceback, math

FRAME_PAUSE_KEY = "_DEFAULT_FRAME_EVENT_PAUSE_KEY"

class TimedEvent(object):
    def __init__(self, listener, time, repeating, args, kwargs):
        try:
            callablename = listener.__name__
        except AttributeError:
            callablename = "GENERIC_UNNAMED_FUNCTION"
        self.eventid = generateUniqueID(callablename + "_FRAME_BASED_EVENT_)
        self.listener = listener
        self.time = max(1, int(math.ceil(time))) #just in case a float was passed
        self.repeating = repeating
        self.lookupindex = None
        self.paused = set()
        self.pause_time = self.time
        self.args = args
        self.kwargs = kwargs
        self.delete_me = False
        self._unscheduled = False

    def call_listener(self):
        if self._unscheduled:
            self.delete_me = True
            return
        if self.paused:
            return
        try:
            self.listener(*self.args, **self.kwargs)
        except Exception as e:
            from kaiengine.debug import debugMessage
            debugMessage(traceback.format_exc())
            debugMessage("something broke with a scheduled listener; deleting it")
            debugMessage(e)
            self.delete_me = True
        if not self.repeating:
            self.delete_me = True


    def pauseEvent(self, time, key = FRAME_PAUSE_KEY):
        self.paused.add(key)
        self.pause_time = max(self.pause_time, time)

    def unpauseEvent(self, key = FRAME_PAUSE_KEY):
        self.paused.discard(key)

    def unschedule(self):
        self.listener = None
        self._unscheduled = True
        self.delete_me = True


class RealtimeEvent(object):
    def __init__(self, listener, time, repeating, scheduler_time, args, kwargs):
        try:
            callablename = listener.__name__
        except AttributeError:
            callablename = "GENERIC_UNNAMED_FUNCTION"
        self.eventid = generateUniqueID(callablename + "_REALTIME_EVENT_)
        self.listener = listener
        self.time = time
        self.repeating = repeating
        self.key = None
        self.handle = None
        self.args = args
        self.kwargs = kwargs
        self.paused = False
        self.time_active = Timer()
        self.pause_timer = Timer()
        self.time_active.Start()
        self.scheduler_time = scheduler_time
        self._destroyed = False
        self._repeat_started = False

    def pauseEvent(self):
        if not self.paused:
            self.paused = True
            if self.handle:
                self.handle.cancel()
            self.time_active.pauseTimer()
            self.pause_timer.Start()

    def unpauseEvent(self):
        returnval = 0.0
        if self.paused:
            self.paused = False
            self.time_active.unpauseTimer()
            returnval = self.pause_timer.checkTime()
            self.pause_timer.stopTimer()
        return returnval

    def destroy(self):
        self._destroyed = True
        if self.handle:
            self.handle.cancel()
            
    def __del__(self):
        self.destroy()

realtimeEvents = {}

def _scheduleRealtime(listener, time, repeat = False, *args, **kwargs):
    scheduler = getGameScheduler()
    newevent = RealtimeEvent(listener, time, repeat, scheduler.time(), args, kwargs)
    handle = scheduler.call_later(time, functools.partial(_realtimeEventRun, newevent, *args, **kwargs))
    try:
        key = realtimeEvents[listener].append(newevent)
    except KeyError:
        realtimeEvents[listener] = sDict()
        key = realtimeEvents[listener].append(newevent)
    realtimeEvents[listener][key].key = key
    realtimeEvents[listener][key].handle = handle
    return newevent.eventid

def _realtimeEventRun(event, *args, **kwargs):
    event.listener(getGameScheduler().time() - event.time, *args, **kwargs)
    _cleanupRealtimeScheduledEvent(event.listener, event.key)
    if not event._destroyed and event.repeating:
        _scheduleRealtime(event.listener, event.time, event.repeating, *args, **kwargs)
        
        
def _unscheduleRealtime(listener):
    try:
        _cleanupRealtimeScheduledEvent(listener, min(realtimeEvents[listener].keys()))
    except (KeyError, ValueError):
        pass
    
def _cleanupRealtimeScheduledEvent(listener, key):
    try:
        if realtimeEvents[listener][key].handle:
            realtimeEvents[listener][key].handle.cancel()
        del realtimeEvents[listener][key] #deliberately do not call destroy method so that repeating ones work. I know this is hacky; I'm sorry
        if not realtimeEvents[listener]:
            del realtimeEvents[listener]
    except KeyError:
        pass

def _realtimeRunOnce(time, event, *args, **kwargs): #this is used so we can catch the call and delete the event
    try:
        run = not event._destroyed
        _cleanupRealtimeEvent(event)
    except AttributeError:
        run = False
    if run: #only run if not unscheduled
        event.listener(time, *args, **kwargs)

def _pauseRealtimeListener(listener):
    for key in sorted(realtimeEvents.keys()):
        if not realtimeEvent[key].paused:
            realtimeEvent[key].pauseEvent()
            break

def _unpauseRealtimeListener(listener):
    for key in sorted(realtimeEvents.keys()):
        if realtimeEvent[key].paused:
            event = realtimeEvent[key]
            pause_time = event.unpauseEvent()
            event.scheduler_time += pause_time
            getGameScheduler().call_later(event.time - event.time_active.getTime(), functools.partial(_realtimeEventRun, event, *event.args, **event.kwargs))
            break

scheduled_events = {}
scheduled_event_times = {}

def _schedule(listener, time, repeat = False, *args, **kwargs):
    event = TimedEvent(listener, time, repeat, args, kwargs)
    _scheduleAppendEvent(event)
    return event.eventid

def _scheduleAppendEvent(event):
    from .functions import checkCurrentFrame #avoiding circular import
    newtime = checkCurrentFrame() + event.time
    key = _scheduleAddToQueue(event, newtime)
    try: scheduled_event_times[event.listener].append([newtime, key, event])
    except KeyError: scheduled_event_times[event.listener] = [[newtime, key, event]]

def _scheduleAddToQueue(event, newtime):
    try: key = scheduled_events[newtime].append(event)
    except KeyError:
        scheduled_events[newtime] = sDict()
        key = scheduled_events[newtime].append(event)
    return key

def _pauseScheduledListener(listener, *args, **kwargs):
    try:
        for time, key, event in scheduled_event_times[listener]:
            if not event.paused and not event._unscheduled and not event.delete_me:
                from .functions import checkCurrentFrame
                event.pauseEvent(time - checkCurrentFrame(), *args, **kwargs)
                del scheduled_events[time][key]
                break
    except KeyError:
        pass
    
def _pauseListenerWithID(listender, eventid, *args, **kwargs):
    try:
        for time, key, event in scheduled_event_times[listener]:
            if event.eventid == eventid:
                from .functions import checkCurrentFrame
                event.pauseEvent(time - checkCurrentFrame(), *args, **kwargs)
                del scheduled_events[time][key]
                break
    except KeyError:
        pass

def _unpauseScheduledListener(listener, *args, **kwargs):
    try:
        time = None
        key = None
        unpausedevent = None
        counter = 0
        for oldtime, oldkey, event in scheduled_event_times[listener]:
            if event.paused:
                event.unpauseEvent(*args, **kwargs)
                if not event.paused:
                    from .functions import checkCurrentFrame
                    time = event.pause_time + checkCurrentFrame()
                    key = _scheduleAddToQueue(event, time)
                    unpausedevent = event
                    event.pause_time = 0
                break
            counter += 1
        if time is not None:
            scheduled_event_times[listener][counter] = (time, key, unpausedevent)
    except KeyError:
        pass

def _unschedule(listener):
    try:
        time, key, event = scheduled_event_times[listener].pop(0)
        event.unschedule()
        del scheduled_events[time][key]
        if len(scheduled_event_times[listener]) == 0: raise IndexError #silly hack to avoid repeated code
    except KeyError: pass
    except IndexError: del scheduled_event_times[listener]
    
def _unscheduleWithID(listener, eventid):
    try:
        for time, key, event in scheduled_event_times[listener]:
            if event.eventid == eventid:
                event.unschedule()
                del scheduled_events[time][key]
                if len(scheduled_event_times[listener]) == 0:
                    del scheduled_event_times[listener]
                break
    except KeyError:
        pass

def _checkSchedule(currentFrame):
    try:
        for event in list(scheduled_events[currentFrame].values()):
            try:
                event.call_listener()
                try:
                    del scheduled_event_times[event.listener][0]
                    if len(scheduled_event_times[event.listener]) == 0: raise IndexError #silly hack to avoid repeated code
                except IndexError: del scheduled_event_times[event.listener]
                except KeyError: pass
                if not event.delete_me:
                    _scheduleAppendEvent(event)
            except:
                import traceback
                traceback.print_exc()
        del scheduled_events[currentFrame]
    except KeyError:
        pass

def _clearSchedule():
    scheduled_events.clear()
    scheduled_event_times.clear()
