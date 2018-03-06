#timer class for frame based timing


from .functions import checkCurrentFrame


class FrameTimer(object):
    def __init__(self):
        self.framestart = -1
        self.pauseframe = -1
        self.countdowntime = -1
        self.started = False
        self.paused = False
        self.countingdown = False


    def Start(self):
        self.stopTimer()
        self.framestart = checkCurrentFrame()
        self.started = True

    def setTime(self, time):
        self.framestart = checkCurrentFrame() - time - self.getPauseTime()

    def countdownStart(self, frames):
        self.Start()
        self.countdowntime = max(frames, 0)

    def pauseTimer(self):
        if not self.paused and self.started:
            self.paused = True
            self.pauseframe = checkCurrentFrame()

    def unpauseTimer(self):
        if self.paused and self.started:
            self.framestart += self.getPauseTime()
            self.paused = False

    def stopTimer(self):
        self.started = False
        self.paused = False
        self.countdowntime = -1

    def checkStarted(self):
        return self.started

    def checkPaused(self):
        return self.paused

    def checkTime(self):
        if self.started:
            if not self.paused:
                return checkCurrentFrame() - self.framestart
            return self.pauseframe - self.framestart
        return 0

    def Tick(self):
        returntime = self.checkTime()
        self.Start()
        return returntime

    def getPauseTime(self):
        if self.paused:
            return checkCurrentFrame() - self.pauseframe
        else:
            return 0

    def checkCountdown(self):
        if self.countdowntime > 0:
            if self.checkTime() < self.countdowntime:
                return False
        return True

    def getCountdownRemaining(self):
        if not self.checkCountdown():
            return self.countdowntime - self.checkTime()
        return 0

    def getCountdownPercent(self):
        return float(self.getCountdownRemaining()) / self.countdowntime
