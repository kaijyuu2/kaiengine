
from .sleep_interface import SleepInterface

from kaiengine.timer import schedule, unschedule, scheduleRealtime, unscheduleRealtime, pauseScheduledListener, pauseScheduledListenerWithID, unpauseScheduledListener, unpauseScheduledListenerWithID, pauseRealtimeListener, unpauseRealtimeListener

from collections import defaultdict

SI_SLEEP_KEY = "_SCHEDULER_INTERFACE_SLEEP_KEY"

class SchedulerInterface(SleepInterface):
    def __init__(self, *args, **kwargs):
        super(SchedulerInterface, self).__init__(*args, **kwargs)
        self._scheduled_methods = defaultdict(int)
        self._scheduled_method_keys = defaultdict(set)
        self._scheduled_realtime_methods = defaultdict(int)
        self._scheduled_realtime_method_keys = defaultdict(set)

    def schedule(self, method, *args, **kwargs):
        if not self.destroyed:
            self._scheduled_method_keys[method].add(schedule(method, *args, **kwargs))
            self._scheduled_methods[method] += 1

    def scheduleUnique(self, method, *args, **kwargs): #won't schedule the same method twice
        if method not in self._scheduled_methods:
            self.schedule(method, *args, **kwargs)

    def unschedule(self, method):
        key = unschedule(method)
        if key is not None: #figured the conditional would be faster overall than searching the list each time a needless unschedule was called
            self._scheduled_method_keys[method].discard(key)
            if not self._scheduled_method_keys[method]:
                del self._scheduled_method_keys[method]
        try:
            self._scheduled_methods[method] -= 1
            if self._scheduled_methods[method] <= 0:
                del self._scheduled_methods[method]
        except (AttributeError, KeyError): pass

    def pauseScheduledListener(self, *args, **kwargs):
        pauseScheduledListener(*args, **kwargs)
        
    def pauseScheduledListenerWithID(self, *args, **kwargs):
        pauseScheduledListenerWithID(*args, **kwargs)

    def pauseAllScheduledListeners(self, *args, **kwargs):
        for method, keyset in self._scheduled_method_keys.items():
            for key in keyset:
                self.pauseScheduledListenerWithID(method, key, *args, **kwargs)

    def unpauseScheduledListener(self, listener, *args, **kwargs):
        unpauseScheduledListener(listener, *args, **kwargs)
        
    def unpauseScheduledListenerWithID(self, *args, **kwargs):
        unpauseScheduledListenerWithID(*args, **kwargs)

    def unpauseAllScheduledListeners(self, *args, **kwargs):
        for method, keyset in self._scheduled_methods_keys.items():
            for key in keyset:
                self.unpauseScheduledListenerWithID(method, key, *args, **kwargs)

    def scheduleRealtime(self, method, *args, **kwargs):
        if not self.destroyed:
            self._scheduled_realtime_method_keys[method].add(scheduleRealtime(method, *args, **kwargs))
            self._scheduled_realtime_methods[method] += 1

    def scheduleRealtimeUnique(self, method, *args, **kwargs):
        if method not in self._scheduled_realtime_methods:
            self.scheduleRealtime(method, *args, **kwargs)

    def unscheduleRealtime(self, method):
        key = unscheduleRealtime(method)
        if key is not None:
            self._scheduled_realtime_method_keys[method].discard(key)
            if not self._scheduled_realtime_method_keys[method]:
                del self._scheduled_realtime_method_keys[method]
        try:
            self._scheduled_realtime_methods[method] -= 1
            if self._scheduled_realtime_methods[method] <= 0:
                del self._scheduled_realtime_methods[method]
        except (AttributeError, KeyError): pass

    def pauseRealtimeListener(self, *args, **kwargs):
        pauseRealtimeListener(*args, **kwargs)
        
    def pauseRealtimeListenerWithID(self, *args, **kwargs):
        pauseRealtimeListenerWithID(*args, **kwargs)

    def pauseAllRealtimeListeners(self, *args, **kwargs):
        for method, keyset in self._scheduled_realtime_method_keys.items():
            for key in keyset:
                self.pauseRealtimeListenerWithID(method, key, *args, **kwargs)

    def unpauseRealtimeListener(self, *args, **kwargs):
        unpauseRealtimeListener(*args, **kwargs)

    def unpauseAllRealtimeListeners(self, *args, **kwargs):
        for method, keyset in self._scheduled_realtime_method_keys.items():
            for key in keyset:
                self.unpauseRealtimeListenerWithID(method, key, *args, **kwargs)

    def unscheduleAllListeners(self):
        if unschedule is not None and unscheduleRealtime is not None:
            for method, val in list(self._scheduled_methods.items()):
                for i in range(val):
                    unschedule(method)
            for method, val in list(self._scheduled_realtime_methods.items()):
                for i in range(val):
                    unscheduleRealtime(method)
        self._scheduled_methods.clear()
        self._scheduled_method_keys.clear()
        self._scheduled_realtime_methods.clear()
        self._scheduled_realtime_method_keys.clear()
        
        
    #overwritten stuff
    
    def sleep(self, *args, **kwargs):
        super().sleep(*args, **kwargs)
        self.pauseAllScheduledListeners(SI_SLEEP_KEY)
        self.pauseAllRealtimeListeners(SI_SLEEP_KEY)
        
    def wakeUp(self, *args, **kwargs):
        super().wakeUp(*args, **kwargs)
        if not self.sleeping:
            self.unpauseAllScheduledListeners(SI_SLEEP_KEY)
            self.unpauseAllRealtimeListeners(SI_SLEEP_KEY)
    

    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        self.unscheduleAllListeners()
