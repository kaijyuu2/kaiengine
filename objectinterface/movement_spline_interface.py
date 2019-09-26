

from .position_interface import PositionInterface
from .schedulerinterface import SchedulerInterface

from kaiengine.timer import Timer, FrameTimer
from kaiengine.gconfig import *
from kaiengine import settings

import math

MI_SPLINE_PAUSE_KEY = "_DEFAULT_MOVEMENT_INTERFACE_SPLINE_PAUSE_KEY"
MIS_SLEEP_PAUSE_KEY = "_MOVEMENT_INTERFACE_SPLINE_SLEEP_PAUSE_KEY"

def getSplinePos(perc_time, start_pos, start_mag, end_pos, end_mag):
    start_pos = float(start_pos)
    end_pos = float(end_pos)
    start_mag = float(start_mag)
    end_mag = float(end_mag)
    perc_time_pow_2 = pow(perc_time,2)
    perc_time_pow_3 = pow(perc_time,3)
    return ((perc_time_pow_3*2 - perc_time_pow_2*3 + 1) * start_pos +
            (perc_time_pow_3 - perc_time_pow_2*2 + perc_time) * start_mag +
            (perc_time_pow_2*3 - perc_time_pow_3*2) * end_pos +
            (perc_time_pow_3 - perc_time_pow_2) * end_mag)

class _MovementSplineInterfaceBase(PositionInterface, SchedulerInterface):
    def __init__(self, *args, **kwargs):
        super(_MovementSplineInterfaceBase, self).__init__(*args, **kwargs)
        self._spline_start_pos = None
        self._spline_end_pos = None
        self._spline_mag = None
        self._pause_movement = set()

        self._spline_countdown_timer = None

    def splineOverTime(self, time, endx, endy, startx = None, starty = None, xmag1 = 0, xmag2 = 0, ymag1 = 0, ymag2 = 0):
        if startx is None: startx = self.pos[0]
        if starty is None: starty = self.pos[1]
        self.unscheduleSplineEvent(self._splineUpdate)
        self._spline_start_pos = (startx, starty)
        self._spline_end_pos = (endx, endy)
        if time <= 0.0:
            self.finishSpline()
        else:
            self._spline_mag1 = (xmag1, ymag1)
            self._spline_mag2 = (ymag2, ymag2)
            self._startSplineTimer(time)
            self.scheduleSplineEvent(self._splineUpdate, 0, True)


    def splineToPoint(self, time, endx, endy, maxspeed = 10000000000, minspeed = 0, xmag1 = 0, xmag2 = 0, ymag1 = 0, ymag2 = 0):
        if time <= 0:
            self._spline_end_pos = (endx,endy)
            self.finishSpline()
        else:
            oldx, oldy = self.pos[:]
            xdistance = endx - oldx
            ydistance = endy - oldy
            xspeed = xdistance / time
            yspeed = ydistance / time
            absspeed = math.sqrt(xspeed**2 + yspeed**2)
            if absspeed > maxspeed:
                xspeed = xdistance / maxspeed
                yspeed = ydistance / maxspeed
                time = maxspeed
            elif absspeed < minspeed:
                xspeed = xdistance / minspeed
                yspeed = ydistance / minspeed
                time = minspeed
            self.splineOverTime(time, endx, endy, xmag1 = xmag1, xmag2 = xmag2, ymag1 = ymag1, ymag2 = ymag2)

    def splineAtSpeed(self, speed, endx, endy, startx = None, starty = None, xmag1 = 0, xmag2 = 0, ymag1 = 0, ymag2 = 0):
        if startx is None: startx = self.pos[0]
        if starty is None: starty = self.pos[1]
        self.splineOverTime(math.sqrt((endx - startx)**2 + (endy - starty)**2) / speed, endx, endy, startx, starty, xmag1, xmag2, ymag1, ymag2)

    def splineToRelativePoint(self, time, x, y, *args, **kwargs):
        self.splineToPoint(time, x + self.pos[0], y + self.pos[1], *args, **kwargs)

    def splineToRelativePointSpeed(self, speed, x, y, *args, **kwargs):
        self.splineAtSpeed(speed, self.pos[0] + x, self.pos[1] + y, None, None, *args, **kwargs)

    def _splineUpdate(self):
        perc_time = 1.0 - self._spline_countdown_timer.getCountdownPercent()
        if perc_time < 1.0:
            self.setPos(*[getSplinePos(perc_time,self._spline_start_pos[i],self._spline_mag1[i], self._spline_end_pos[i], self._spline_mag2[i]) for i in range(2)])
        else:
            self.finishSpline()


    def finishSpline(self):
        if self._spline_end_pos is not None:
            self.setPos(*self._spline_end_pos)
            self.unscheduleSplineEvent(self._splineUpdate)
            self._spline_countdown_timer.stopTimer()
            self._spline_end_pos = None

    def stopSpline(self):
        self._splineUpdate()
        try:
            self._spline_end_pos = self.pos[:]
            self.finishSpline()
        except TypeError:
            pass

    def pauseSpline(self, key = MI_SPLINE_PAUSE_KEY):
        self._pause_movement.add(key)
        if self.checkSplinePaused():
            self._spline_countdown_timer.pauseTimer()

    def unpauseSpline(self, key = MI_SPLINE_PAUSE_KEY):
        self._pause_movement.discard(key)
        if not self.checkSplinePaused():
            self._spline_countdown_timer.unpauseTimer()

    def checkSplinePaused(self):
        return bool(self._pause_movement)

    def checkSplineActive(self):
        return not self._spline_end_pos is None


    #stuff that should be overwritten

    def getSplineTimeRemaining(self):
        pass

    def getSplineTimeRemainingFrames(self):
        pass

    def _startSplineTimer(self, time):
        pass

    #this this overwrites

    def sleep(self, *args, **kwargs):
        super().sleep(*args, **kwargs)
        self.pauseSpline(MIS_SLEEP_PAUSE_KEY)

    def wakeUp(self, *args, **kwargs):
        super().wakeUp(*args, **kwargs)
        if not self.sleeping:
            self.unpauseSpline(MIS_SLEEP_PAUSE_KEY)

class MovementSplineInterfaceFrames(_MovementSplineInterfaceBase):

    def __init__(self, *args, **kwargs):
        super(MovementSplineInterfaceFrames, self).__init__(*args, **kwargs)
        self.scheduleSplineEvent = self.schedule
        self.unscheduleSplineEvent = self.unschedule
        self._spline_countdown_timer = FrameTimer()

    def getSplineTimeRemaining(self):
        return float(self.getTimeRemainingFrames()) / settings.getValue(DYNAMIC_SETTINGS_FRAMES_PER_SECOND)

    def getSplineTimeRemainingFrames(self):
        return self._spline_countdown_timer.getCountdownRemaining()

    def _startSplineTimer(self, time):
        self._spline_countdown_timer.countdownStart(int(time * settings.getValue(DYNAMIC_SETTINGS_FRAMES_PER_SECOND)))


class MovementSplineInterfaceRealtime(_MovementSplineInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(MovementSplineInterfaceRealtime, self),__init__(*args, **kwargs)
        self.scheduleSplineEvent = self.scheduleRealtime
        self.unscheduleSplineEvent = self.unscheduleRealtime
        self._spline_countdown_timer = Timer()

    def getSplineTimeRemaining(self):
        return self._spline_countdown_timer.getCountdownRemaining()

    def getSplineTimeRemainingFrames(self):
        """not super accurate; will be AT LEAST this many frames, though maybe one less"""
        return int(math.ceil(self.getCountdownRemaining() * settings.getValue(DYNAMIC_SETTINGS_FRAMES_PER_SECOND)))


    def _startSplineTimer(self, time):
        self._spline_countdown_timer.countdownStart(time)
