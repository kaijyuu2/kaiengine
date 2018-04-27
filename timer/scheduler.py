
#functions/etc for scheduling logic

from .timer import Timer
from .maingamescheduler import getGameScheduler

from kaiengine.sDict import sDict


import functools
import traceback, math

class TimedEvent(object):
    def __init__(self, listener, time, repeating, args, kwargs):
        self.listener = listener
        self.time = max(1, int(math.ceil(time))) #just in case a float was passed
        self.repeating = repeating
        self.lookupindex = None
        self.paused = False
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


    def pauseEvent(self, time):
        self.paused = True
        self.pause_time = max(0, time)

    def unpauseEvent(self):
        self.paused = False


    def unschedule(self):
        self.listener = None
        self._unscheduled = True
        self.delete_me = True


class RealtimeEvent(object):
    def __init__(self, listener, time, repeating, scheduler_time, args, kwargs):
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


scheduledEvents = {}
scheduledEventTimes = {}

def _Schedule(listener, time, repeat = False, *args, **kwargs):
    _ScheduleAppendEvent(TimedEvent(listener, time, repeat, args, kwargs))

def _ScheduleAppendEvent(event):
    from .functions import checkCurrentFrame #avoiding circular import
    newtime = checkCurrentFrame() + event.time
    key = _ScheduleAddToQueue(event, newtime)
    try: scheduledEventTimes[event.listener].append([newtime, key, event])
    except KeyError: scheduledEventTimes[event.listener] = [[newtime, key, event]]

def _ScheduleAddToQueue(event, newtime):
    try: key = scheduledEvents[newtime].append(event)
    except KeyError:
        scheduledEvents[newtime] = sDict()
        key = scheduledEvents[newtime].append(event)
    return key

def _PauseScheduledListener(listener):
    try:
        for time, key, event in scheduledEventTimes[listener]:
            if not event.paused and not event._unscheduled and not event.delete_me:
                from .functions import checkCurrentFrame
                event.pauseEvent(time - checkCurrentFrame())
                del scheduledEvents[time][key]
                break
    except KeyError:
        pass

def _UnpauseScheduledListener(listener):
    try:
        time = None
        key = None
        unpausedevent = None
        counter = 0
        for oldtime, oldkey, event in scheduledEventTimes[listener]:
            if event.paused:
                event.unpauseEvent()
                from .functions import checkCurrentFrame
                time = event.pause_time + checkCurrentFrame()
                key = _ScheduleAddToQueue(event, time)
                unpausedevent = event
                break
            counter += 1
        if time is not None:
            scheduledEventTimes[listener][counter] = (time, key, unpausedevent)
    except KeyError:
        pass

def _Unschedule(listener):
    try:
        time, key, event = scheduledEventTimes[listener].pop(0)
        event.unschedule()
        del scheduledEvents[time][key]
        if len(scheduledEventTimes[listener]) == 0: raise IndexError #silly hack to avoid repeated code
    except KeyError: pass
    except IndexError: del scheduledEventTimes[listener]

def _checkSchedule(currentFrame):
    try:
        for event in list(scheduledEvents[currentFrame].values()):
            try:
                event.call_listener()
                try:
                    del scheduledEventTimes[event.listener][0]
                    if len(scheduledEventTimes[event.listener]) == 0: raise IndexError #silly hack to avoid repeated code
                except IndexError: del scheduledEventTimes[event.listener]
                except KeyError: pass
                if not event.delete_me:
                    _ScheduleAppendEvent(event)
            except:
                import traceback
                traceback.print_exc()
        del scheduledEvents[currentFrame]
    except KeyError:
        pass

def _ClearSchedule():
    global scheduledEventTimes
    scheduledEvents.clear()
    scheduledEventTimes.clear()
