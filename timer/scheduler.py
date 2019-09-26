
#functions/etc for scheduling logic

from .timer import Timer
from .maingamescheduler import getGameScheduler

from kaiengine.sDict import sDict
from kaiengine.uidgen import generateUniqueID

import functools
import traceback, math

FRAME_PAUSE_KEY = "_DEFAULT_FRAME_EVENT_PAUSE_KEY"
REALTIME_PAUSE_KEY = "_DEFAULT_REALTIME_EVENT_PAUSE_KEY"

class TimedEvent(object):
    def __init__(self, listener, time, repeating, args, kwargs):
        try:
            callablename = listener.__name__
        except AttributeError:
            callablename = "GENERIC_UNNAMED_FUNCTION"
        self.eventid = generateUniqueID(callablename + "_FRAME_BASED_EVENT_")
        self.listener = listener
        self.time = max(1, int(math.ceil(time))) #just in case a float was passed
        self.key = None
        self.repeating = repeating
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
            if self.listener(*self.args, **self.kwargs):
                self.delete_me = True
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

    def destroy(self):
        self.unschedule()

    def __del__(self):
        self.destroy()


class RealtimeEvent(object):
    def __init__(self, listener, time, repeating, args, kwargs):
        try:
            callablename = listener.__name__
        except AttributeError:
            callablename = "GENERIC_UNNAMED_FUNCTION"
        self.eventid = generateUniqueID(callablename + "_REALTIME_EVENT_")
        self.listener = listener
        self.time = time
        self.repeating = repeating
        self.key = None
        self.handle = None
        self.args = args
        self.kwargs = kwargs
        self.paused = set()
        self.time_active = Timer()
        self.pause_timer = Timer()
        self.time_active.Start()
        self.scheduler_time = 0
        self._destroyed = False
        self._repeat_started = False

    def pauseEvent(self, key = REALTIME_PAUSE_KEY):
        self.paused.add(key)
        if self.handle:
            self.handle.cancel()
        if not self.pause_timer.started:
            self.time_active.pauseTimer()
            self.pause_timer.Start()

    def unpauseEvent(self, key = REALTIME_PAUSE_KEY):
        returnval = 0.0
        self.paused.discard(key)
        if not self.paused:
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

realtime_events = {} #contains the realtime events, indexed by event id
realtime_events_listener_map = {} #indexed by listener, contains event ids in sDict

def _scheduleRealtime(listener, time, repeat = False, *args, **kwargs):
    newevent = RealtimeEvent(listener, time, repeat, args, kwargs)
    _scheduleRealtimeWithEvent(newevent)

def _scheduleRealtimeWithEvent(newevent, *args, **kwargs):
    scheduler = getGameScheduler()
    handle = scheduler.call_later(newevent.time, functools.partial(_realtimeEventRun, newevent, *args, **kwargs))
    realtime_events[newevent.eventid] = newevent
    newevent.handle = handle
    try:
        key = realtime_events_listener_map[newevent.listener].append(newevent.eventid)
    except KeyError:
        realtime_events_listener_map[newevent.listener] = sDict()
        key = realtime_events_listener_map[newevent.listener].append(newevent.eventid)
    newevent.key = key
    newevent.scheduler_time = scheduler.time()
    return newevent.eventid

def _realtimeEventRun(event, *args, **kwargs):
    try:
        event.listener(getGameScheduler().time() - event.scheduler_time, *args, **kwargs)
    except:
        from kaiengine.debug import debugMessage
        import traceback
        debugMessage("Something broke with a scheduled realtime listener; deleting it.")
        traceback.print_exc()
        event.repeating = False #stop it from repeating
    _cleanupRealtimeScheduledEvent(event.eventid)
    if not event._destroyed:
        if event.repeating:
            _scheduleRealtimeWithEvent(event, *args, **kwargs)
        else:
            _destroyRealtimeEvent(event.eventid)

def _unscheduleRealtime(listener):
    try:
        ID = realtime_events_listener_map[listener].pop(realtime_events_listener_map[listener].firstKey(), None)
        if ID is not None:
            return _unscheduleRealtimeByID(ID)
        else: #assist in leak prevention
            if not realtime_events_listener_map[listener]:
                del realtime_events_listener_map[listener]
    except KeyError:
        pass
    return None


def _unscheduleRealtimeByID(eventid):
    _cleanupRealtimeScheduledEvent(eventid)
    try:
        _destroyRealtimeEvent(eventid)
    except KeyError:
        pass
    return eventid

def _cleanupRealtimeScheduledEvent(eventid):
    try:
        event = realtime_events[eventid]
        try:
            realtime_events_listener_map[event.listener].pop(event.key, None)
            if not realtime_events_listener_map[event.listener]:
                del realtime_events_listener_map[event.listener]
        except KeyError:
            pass
        if event.handle:
            event.handle.cancel()
    except KeyError:
        pass

def _destroyRealtimeEvent(eventid):
    realtime_events[eventid].destroy()
    del realtime_events[eventid]

def _pauseRealtimeListener(listener, *args, **kwargs):
    try:
        _pauseRealtimeListenerWithID(realtime_events_listener_map[listener], *args, **kwargs)
    except KeyError:
        pass

def _pauseRealtimeListenerWithID(eventid, *args, **kwargs):
    try:
        realtime_events[eventid].pauseEvent(*args, **kwargs)
    except KeyError:
        pass

def _unpauseRealtimeListener(listener, *args, **kwargs):
    try:
        _unpauseRealtimeListenerWithID(realtime_events_listener_map[listener], *args, **kwargs)
    except KeyError:
        pass

def _unpauseRealtimeListenerWithID(eventid, *args, **kwargs):
    try:
        event = realtime_events[eventid]
        pause_time = event.unpauseEvent(*args, **kwargs)
        if not event.paused:
            event.scheduler_time += pause_time
            getGameScheduler().call_later(event.time - event.time_active.getTime(), functools.partial(_realtimeEventRun, event, *event.args, **event.kwargs))
    except KeyError:
        pass

scheduled_events = {} #contains event, indexed by eventid
scheduled_events_time_map = {} #contains unordered eventid set, indexed by time
scheduled_events_listener_map = {} #contains eventid sdict (ordered oldest to newest), indexed by listener
scheduled_events_id_map = {} #contains time, indexed by eventid

def _schedule(listener, time, repeat = False, *args, **kwargs):
    event = TimedEvent(listener, time, repeat, args, kwargs)
    scheduled_events[event.eventid] = event
    _scheduleAppendEvent(event)
    return event.eventid

def _scheduleAppendEvent(event):
    from .functions import checkCurrentFrame #avoiding circular import
    newtime = checkCurrentFrame() + event.time
    _scheduleAddToQueue(event, newtime)
    try: key = scheduled_events_listener_map[event.listener].append(event.eventid)
    except KeyError:
        scheduled_events_listener_map[event.listener] = sDict()
        key = scheduled_events_listener_map[event.listener].append(event.eventid)
    scheduled_events_listener_map[event.listener].pop(event.key, None) #get rid of old if it exists
    event.key = key

def _scheduleAddToQueue(event, newtime):
    try: scheduled_events_time_map[newtime].add(event.eventid)
    except KeyError:
        scheduled_events_time_map[newtime] = set()
        scheduled_events_time_map[newtime].add(event.eventid)
    scheduled_events_id_map[event.eventid] = newtime

def _pauseScheduledListener(listener, *args, **kwargs):
    try:
        ID = scheduled_events_listener_map[listener].firstItem()
        _pauseScheduledListenerWithID(ID, *args, **kwargs)
    except (KeyError, IndexError):
        pass

def _pauseScheduledListenerWithID(ID, *args, **kwargs):
    from .functions import checkCurrentFrame #avoiding circular import
    try:
        time = scheduled_events_id_map[ID]
        scheduled_events[ID].pauseEvent(time - checkCurrentFrame(), *args, **kwargs)
        scheduled_events_time_map[time].discard(ID)
    except KeyError:
        pass


def _unpauseScheduledListener(listener, *args, **kwargs):
    try:
        ID = scheduled_events_listener_map[listener].firstItem()
        _unpauseScheduledListenerWithID(ID, *args, **kwargs)
    except (KeyError, IndexError):
        pass

def _unpauseScheduledListenerWithID(ID, *args, **kwargs):
    try:
        event = scheduled_events[ID]
        event.unpauseEvent(*args, **kwargs)
        if not event.paused:
            from .functions import checkCurrentFrame
            _scheduleAddToQueue(event, event.pause_time + checkCurrentFrame())
    except KeyError:
        pass


def _unschedule(listener):
    try:
        ID = scheduled_events_listener_map[listener].firstItem()
        if ID not in scheduled_events: #additional leak check in case of error
            scheduled_events_listener_map[listener].pop(scheduled_events_listener_map[listener].firstKey(), None)
            if not scheduled_events_listener_map[listener]:
                del scheduled_events_listener_map[listener]
            return ID
        else:
            return _unscheduleWithID(ID)
    except (KeyError, IndexError):
        return None

def _unscheduleWithID(ID):
    #do our best to prevent any possible leaks in case of error
    event = scheduled_events.pop(ID, None)
    time = scheduled_events_id_map.pop(ID, None)
    if event is not None:
        try:
            scheduled_events_listener_map[event.listener].pop(event.key, None)
            if not scheduled_events_listener_map[event.listener]:
                del scheduled_events_listener_map[event.listener]
        except KeyError:
            pass
        event.destroy()
    try:
        scheduled_events_time_map[time].discard(ID)
    except KeyError:
        pass
    return ID


def _checkSchedule(currentFrame):
    try:
        for eventid in list(scheduled_events_time_map[currentFrame]): #make copy as a list so as to not have iteration errors
            try:
                event = scheduled_events[eventid]
                try:
                    event.call_listener()
                    if not event.delete_me:
                        _scheduleAppendEvent(event)
                    else:
                        _unscheduleWithID(eventid)
                except:
                    import traceback
                    traceback.print_exc()
            except KeyError:
                pass
        del scheduled_events_time_map[currentFrame]
    except KeyError:
        pass

def _clearSchedule():
    scheduled_events.clear()
    scheduled_events_listener_map.clear()
    scheduled_events_time_map.clear()
    scheduled_events_id_map.clear()
