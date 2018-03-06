

from .timer import Timer

from kaiengine.sDict import sDict
from kaiengine.debug import debugMessage

from pyglet import clock

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
    def __init__(self, listener, time, repeating, args, kwargs):
        self.listener = listener
        self.time = time
        self.repeating = repeating
        self.key = None
        self.args = args
        self.kwargs = kwargs
        self.paused = False
        self.time_active = Timer()
        self.time_active.Start()
        self.pause_time = 0.0
        self._destroyed = False
        self._repeat_started = False

    def pauseEvent(self):
        self.paused = True
        self.pause_time = self.time - (self.time_active.checkTime() % self.time)
        self.time_active.pauseTimer()
        if self._repeat_started:
            self._repeat_started = False
            clock.unschedule(self.repeatRestart)

    def unpauseEvent(self):
        if not self.paused:
            self.paused = True
            self.time_active.unpauseTimer()
            if self.repeating:
                clock.schedule_once(self.repeatRestart, self.pause_time)
            else:
                clock.schedule_once(self.listener, self.pause_time, *self.args, **self.kwargs)

    def repeatRestart(self):
        clock.schedule_interval(self.listener, self.time, *self.args, **self.kwargs)
        self._repeat_started = True

    def destroy(self):
        self._destroyed = True
        if self._repeat_started:
            self._repeat_started = False
            clock.unschedule(self.repeatRestart) #very slow call; do sparingly

realtimeEvents = {}

def _ScheduleRealtime(listener, time, repeat = False, *args, **kwargs):
    newevent = RealtimeEvent(listener, time, repeat, args, kwargs)
    try:
        key = realtimeEvents[listener].append(newevent)
    except KeyError:
        realtimeEvents[listener] = sDict()
        key = realtimeEvents[listener].append(newevent)
    realtimeEvents[listener][key].key = key
    if repeat:
        clock.schedule_interval(listener, time, *args, **kwargs)
    else:
        clock.schedule_once(_realtimeRunOnce, time, newevent, *args, **kwargs)

def _realtimeRunOnce(time, event, *args, **kwargs): #this is used so we can catch the call and delete the event
    try:
        run = not event._destroyed
        _cleanupRealtimeEvent(event)
    except AttributeError:
        run = False
    if run: #only run if not unscheduled
        event.listener(time, *args, **kwargs)

def _PauseRealtimeListener(listener):
    clock.unschedule(listener)
    try:
        for event in realtimeEvents[listener].values():
            if not event.paused and (event.repeating or event.time >= event.time_active.checkTime()):
                event.pauseEvent()
                break
    except KeyError: pass

def _UnpauseRealtimeListener(listener):
    try:
        for event in realtimeEvents[listener].values():
            if event.paused and (event.repeating or event.time >= event.time_active.checkTime()):
                event.unpauseEvent()
                break
    except KeyError: pass

def _UnscheduleRealtime(listener):
    last_repeating = False
    try:
        deletekeys = []
        for key, event in realtimeEvents[listener].items(): #clears out junk too
            deletekeys.append(key)
            event.destroy()
            last_repeating = event.repeating
            if event.repeating or event.time >= event.time_active.checkTime():
                break
        for key in deletekeys:
            del realtimeEvents[listener][key]
        if not realtimeEvents[listener]:
            del realtimeEvents[listener]
    except KeyError: pass
    if last_repeating: #only call unschedule for repeating functions, since unschedule so slow
        clock.unschedule(listener)

def _cleanupRealtimeEvent(event):
    event.destroy()
    try:
        del realtimeEvents[event.listener][event.key]
    except KeyError:
        pass
    try:
        if not realtimeEvents[event.listener]:
            del realtimeEvents[event.listener]
    except KeyError:
        pass

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
