

from pyglet.clock import Clock
#for controlling time

class MainTimer(object): #main timer everything synchronizes to
    def __init__(self):
        self.clock = Clock()
        self.clock.tick()
        self.time_elapsed = 0.0
        self.pause_time = 0.0
        self.last_tick = 0.0
        self.global_pause = False

    def Tick(self):
        if self.global_pause:
            self.last_tick = 0.0
            return self.pause_time
        self.last_tick = self.clock.tick()
        self.time_elapsed += self.last_tick
        return self.time_elapsed

    def pauseTimer(self):
        if not self.global_pause:
            self.pause_time = self.tick()
            self.global_pause = True

    def unpauseTimer(self):
        if self.global_pause:
            self.clock.tick()
            self.global_pause = False

gametimer = MainTimer()


class Timer(object):
    def __init__(self):
        self.paused = True
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0
        self.pause_time = 0.0

    def Start(self):
        self.unpauseTimer()
        self.start_time = gametimer.Tick()
        self.started = True

    def setTime(self, time):
        self.start_time = gametimer.Tick() - time - self.getPauseTime()

    def stopTimer(self):
        self.unpauseTimer()
        self.started = False

    def pauseTimer(self):
        if not self.paused:
            self.paused = True
            self.pause_time = gametimer.Tick()

    def unpauseTimer(self):
        if self.paused:
            time_difference = self.getPauseTime()
            self.start_time += time_difference
            self.end_time += time_difference
            self.paused = False

    def checkPaused(self):
        return self.paused

    def countdownStart(self, time):
        self.Start()
        self.end_time = float(self.start_time + time)

    def checkCountdown(self):
        if self.started:
            if self.getCountdownTime() <= 0.0:
                return True
        return False

    def getCountdownTime(self):
        if self.started:
            total_time = self.end_time - self.start_time
            time = self.start_time
            if self.paused:
                time += gametimer.Tick() - self.pause_time
            total_time -= gametimer.Tick() - time
            if total_time > 0.0:
                return total_time
        return 0.0

    def getCountdownPercent(self):
        return self.getCountdownTime() / (self.end_time - self.start_time)

    def checkTime(self):
        if self.started:
            time = self.start_time
            if self.paused:
                time += gametimer.Tick() - self.pause_time
            return gametimer.Tick() - time
        return 0.0

    def getPauseTime(self):
        if self.paused:
            return gametimer.Tick() - self.pause_time
        else:
            return 0

    def Tick(self):
        returntime = self.checkTime()
        self.Start()
        return returntime

    #backwards compatibility stuff below

    def start(self):
        self.Start()

    def check_time(self):
        return self.checkTime()

    def tick(self):
        return self.Tick()
