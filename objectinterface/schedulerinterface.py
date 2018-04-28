

from kaiengine.destroyinterface import DestroyInterface

from kaiengine.timer import schedule, unschedule, scheduleRealtime, unscheduleRealtime, pauseScheduledListener, unpauseScheduledListener, pauseRealtimeListener, unpauseRealtimeListener


class SchedulerInterface(DestroyInterface):
    def __init__(self, *args, **kwargs):
        super(SchedulerInterface, self).__init__(*args, **kwargs)
        self._scheduled_methods = {}
        self._scheduled_realtime_methods = {}

    def schedule(self, method, *args, **kwargs):
        if not self.destroyed:
            schedule(method, *args, **kwargs)
            try: self._scheduled_methods[method] += 1
            except KeyError: self._scheduled_methods[method] = 1

    def scheduleUnique(self, method, *args, **kwargs): #won't schedule the same method twice
        if method not in self._scheduled_methods:
            self.schedule(method, *args, **kwargs)

    def unschedule(self, method):
        unschedule(method)
        try:
            self._scheduled_methods[method] -= 1
            if self._scheduled_methods[method] <= 0:
                del self._scheduled_methods[method]
        except (AttributeError, KeyError): pass

    def pauseScheduledListener(self, listener):
        pauseScheduledListener(listener)

    def pauseAllScheduledListeners(self):
        for method, number in list(self._scheduled_methods.items()):
            for i in range(number):
                self.pauseScheduledListener(method)

    def unpauseScheduledListener(self, listener):
        unpauseScheduledListener(listener)

    def unpauseAllScheduledListeners(self):
        for method, number in list(self._scheduled_methods.items()):
            for i in range(number):
                self.unpauseScheduledListener(method)

    def scheduleRealtime(self, method, *args, **kwargs):
        if not self.destroyed:
            scheduleRealtime(method, *args, **kwargs)
            try: self._scheduled_realtime_methods[method] += 1
            except KeyError: self._scheduled_realtime_methods[method] = 1

    def scheduleRealtimeUnique(self, method, *args, **kwargs):
        if method not in self._scheduled_realtime_methods:
            self.scheduleRealtime(method, *args, **kwargs)

    def unscheduleRealtime(self, method):
        unscheduleRealtime(method)
        try:
            self._scheduled_realtime_methods[method] -= 1
            if self._scheduled_realtime_methods[method] <= 0:
                del self._scheduled_realtime_methods[method]
        except (AttributeError, KeyError): pass

    def pauseRealtimeListener(self, method):
        pauseRealtimeListener(method)

    def pauseAllRealtimeListeners(self):
        for method, number in list(self._scheduled_realtime_methods.items()):
            for i in range(number):
                self.pauseRealtimeListener(method)

    def unpauseRealtimeListener(self, method):
        unpauseRealtimeListener(method)

    def unpauseAllRealtimeListeners(self):
        for method, number in list(self._scheduled_realtime_methods.items()):
            for i in range(number):
                self.unpauseRealtimeListener(method)

    def unscheduleAllListeners(self):
        if unschedule is not None and unscheduleRealtime is not None:
            for method, val in list(self._scheduled_methods.items()):
                for i in range(val):
                    unschedule(method)
            for method, val in list(self._scheduled_realtime_methods.items()):
                for i in range(val):
                    unscheduleRealtime(method)
        self._scheduled_methods.clear()
        self._scheduled_realtime_methods.clear()

    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        self.unscheduleAllListeners()
