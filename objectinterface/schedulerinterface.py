
from .sleep_interface import SleepInterface

from kaiengine.timer import schedule, unschedule, scheduleRealtime, unscheduleRealtime, pauseScheduledListener, pauseScheduledListenerWithID, unpauseScheduledListener, unpauseScheduledListenerWithID, pauseRealtimeListener, pauseRealtimeListenerWithID, unpauseRealtimeListener, unpauseRealtimeListenerWithID
from kaiengine.timer import delay, undelay

SI_SLEEP_KEY = "_SCHEDULER_INTERFACE_SLEEP_KEY"

class SchedulerInterface(SleepInterface):
    def __init__(self, *args, **kwargs):
        super(SchedulerInterface, self).__init__(*args, **kwargs)
        self._scheduled_method_keys = set()
        self._scheduled_realtime_method_keys = set()
        self._delayed_methods = set()

    def schedule(self, method, *args, **kwargs):
        if not self.destroyed:
            key = schedule(method, *args, **kwargs)
            self._scheduled_method_keys.add(key)
            return key
        return None

    def scheduleUnique(self, method, *args, **kwargs): #won't schedule the same method twice
        self.unschedule(method)
        return self.schedule(method, *args, **kwargs)

    def unschedule(self, method):
        key = unschedule(method)
        self._scheduled_method_keys.discard(key)
        return key

    def pauseScheduledListener(self, *args, **kwargs):
        pauseScheduledListener(*args, **kwargs)

    def pauseScheduledListenerWithID(self, *args, **kwargs):
        pauseScheduledListenerWithID(*args, **kwargs)

    def pauseAllScheduledListeners(self, *args, **kwargs):
        for key in self._scheduled_method_keys:
            self.pauseScheduledListenerWithID(key, *args, **kwargs)

    def unpauseScheduledListener(self, listener, *args, **kwargs):
        unpauseScheduledListener(listener, *args, **kwargs)

    def unpauseScheduledListenerWithID(self, *args, **kwargs):
        unpauseScheduledListenerWithID(*args, **kwargs)

    def unpauseAllScheduledListeners(self, *args, **kwargs):
        for key in self._scheduled_method_keys:
            self.unpauseScheduledListenerWithID(key, *args, **kwargs)

    def scheduleRealtime(self, method, *args, **kwargs):
        if not self.destroyed:
            key = scheduleRealtime(method, *args, **kwargs)
            self._scheduled_realtime_method_keys.add(key)
            return key
        return None

    def scheduleRealtimeUnique(self, method, *args, **kwargs):
        self.unscheduleRealtime(method)
        return self.scheduleRealtime(method, *args, **kwargs)

    def unscheduleRealtime(self, method):
        key = unscheduleRealtime(method)
        self._scheduled_realtime_method_keys.discard(key)
        return key

    def pauseRealtimeListener(self, *args, **kwargs):
        pauseRealtimeListener(*args, **kwargs)

    def pauseRealtimeListenerWithID(self, *args, **kwargs):
        pauseRealtimeListenerWithID(*args, **kwargs)

    def pauseAllRealtimeListeners(self, *args, **kwargs):
        for key in self._scheduled_realtime_method_keys:
            self.pauseRealtimeListenerWithID(key, *args, **kwargs)

    def unpauseRealtimeListener(self, *args, **kwargs):
        unpauseRealtimeListener(*args, **kwargs)

    def unpauseRealtimeListenerWithID(self, *args, **kwargs):
        unpauseRealtimeListenerWithID(*args, **kwargs)

    def unpauseAllRealtimeListeners(self, *args, **kwargs):
        for key in self._scheduled_realtime_method_keys:
            self.unpauseRealtimeListenerWithID(key, *args, **kwargs)

    def unscheduleAllListeners(self):
        if unschedule is not None and unscheduleRealtime is not None:
            for key in list(self._scheduled_method_keys):
                self.unschedule(key)
            for key in list(self._scheduled_realtime_method_keys):
                self.unscheduleRealtime(key)
        self._scheduled_method_keys.clear()
        self._scheduled_realtime_method_keys.clear()

    def waitForCondition(self, func, condition, *args, **kwargs):
        return self.schedule(self._waitForCondition, 1, True, func, condition, *args, **kwargs)

    def _waitForCondition(self, func, condition, *args, **kwargs):
        if condition():
            func(*args, **kwargs)
            return True

    def delay(self, listener, priority = 0, *args, **kwargs):
        if not self.destroyed:
            ID = delay(listener, priority, *args, **kwargs)
            self._delayed_methods.add(ID)
            return ID
        return None

    def undelay(self, ID):
        ID = undelay(ID)
        self._delayed_methods.discard(ID)

    def undelayAll(self):
        for ID in self._delayed_methods:
            undelay(ID)
        self._delayed_methods.clear()

    #overwritten stuff

    def sleep(self, *args, **kwargs):
        startedsleeping = super().sleep(*args, **kwargs)
        if startedsleeping:
            self.pauseAllScheduledListeners(SI_SLEEP_KEY)
            self.pauseAllRealtimeListeners(SI_SLEEP_KEY)
        return startedsleeping

    def wakeUp(self, *args, **kwargs):
        previouslysleeping = super().wakeUp(*args, **kwargs)
        if previouslysleeping:
            self.unpauseAllScheduledListeners(SI_SLEEP_KEY)
            self.unpauseAllRealtimeListeners(SI_SLEEP_KEY)
        return previouslysleeping


    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        self.unscheduleAllListeners()
        self.undelayAll()
