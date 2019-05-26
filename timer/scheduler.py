
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
    def __init__(self, listener, time, repeating, scheduler_time, args, kwargs):
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
        self.scheduler_time = scheduler_time
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

realtime_events = {}

def _scheduleRealtime(listener, time, repeat = False, *args, **kwargs):
    scheduler = getGameScheduler()
    newevent = RealtimeEvent(listener, time, repeat, scheduler.time(), args, kwargs)
    handle = scheduler.call_later(time, functools.partial(_realtimeEventRun, newevent, *args, **kwargs))
    try:
        key = realtime_events[listener].append(newevent)
    except KeyError:
        realtime_events[listener] = sDict()
        key = realtime_events[listener].append(newevent)
    realtime_events[listener][key].key = key
    realtime_events[listener][key].handle = handle
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
    _cleanupRealtimeScheduledEvent(event.listener, event.key)
    if not event._destroyed and event.repeating:
        _scheduleRealtime(event.listener, event.time, event.repeating, *args, **kwargs)
        
def _unscheduleRealtime(listener):
    eventid = None
    try:
        key = min(realtime_events[listener].keys())
        eventid = realtime_events[listener][key].eventid
        _cleanupRealtimeScheduledEvent(listener, key)
    except (KeyError, ValueError):
        pass
    return eventid

def _unscheduleRealtimeByID(listener, eventid):
    try:
        for key, event in realtime_events[listener].items():
            if event.eventid == eventid:
                _cleanupRealtimeScheduledEvent(listener, key)
                break
    except (KeyError, ValueError):
        pass
    return eventid
    
def _cleanupRealtimeScheduledEvent(listener, key):
    try:
        if realtime_events[listener][key].handle:
            realtime_events[listener][key].handle.cancel()
        del realtime_events[listener][key] #deliberately do not call destroy method so that repeating ones work. I know this is hacky; I'm sorry
        if not realtime_events[listener]:
            del realtime_events[listener]
    except KeyError:
        pass

def _realtimeRunOnce(time, event, *args, **kwargs): #this is used so we can catch the call and delete the event
    try:
        run = not event._destroyed
    except AttributeError:
        run = False
    if run: #only run if not unscheduled
        event.listener(time, *args, **kwargs)
    if event:
        _cleanupRealtimeScheduledEvent(event.listener, event.key)

def _pauseRealtimeListener(listener, *args, **kwargs):
    for key in sorted(realtime_events.keys()):
        if not realtime_events[key].paused:
            realtime_events[key].pauseEvent(*args, **kwargs)
            break
        
def _pauseRealtimeListenerWithID(listener, eventid, *args, **kwargs):
    for key, event in realtime_events.items():
        if event.eventid == eventid:
            realtime_events[key].pauseEvent(*args, **kwargs)
            break

def _unpauseRealtimeListener(listener, *args, **kwargs):
    for key in sorted(realtime_events.keys()):
        if realtime_events[key].paused:
            event = realtime_events[key]
            pause_time = event.unpauseEvent(*args, **kwargs)
            if not event.paused:
                event.scheduler_time += pause_time
                getGameScheduler().call_later(event.time - event.time_active.getTime(), functools.partial(_realtimeEventRun, event, *event.args, **event.kwargs))
            break
        
def _unpauseRealtimeListenerWithID(listener, eventid, *args, **kwargs):
    for event in realtime_events.values():
        if event.eventid == eventid:
            pause_time = event.unpauseEvent(*args, **kwargs)
            if not event.paused:
                event.scheduler_time += pause_time
                getGameScheduler().call_later(event.time - event.time_active.getTime(), functools.partial(_realtimeEventRun, event, *event.args, **event.kwargs))
            break

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
