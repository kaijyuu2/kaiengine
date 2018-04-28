

from .position_interface import PositionInterface
from .schedulerinterface import SchedulerInterface

from kaiengine.timer import getRealtimeSinceLastFrame
from kaiengine.gconfig import *
from kaiengine import settings

import math

MI_PAUSE_KEY = "_DEFAULT_MOVEMENT_INTERFACE_PAUSE_KEY"

class MovementInterfaceBase(PositionInterface, SchedulerInterface):
    def __init__(self, *args, **kwargs):
        super(MovementInterfaceBase, self).__init__(*args, **kwargs)
        self.velocity = (0.0,0.0)
        self.acceleration = (0.0,0.0)
        self._move_to_point_end = None
        self._pause_movement = set()


    def moveOverTime(self, time, xvel = 0, yvel = 0, xaccel = 0, yaccel = 0):
        self.setVelocity(xvel, yvel)
        self.setAcceleration(xaccel, yaccel)
        self.scheduleMovementEvent(self.finishMovement, self._MovementGetWaitTime(time))

    def moveToPoint(self, time, x, y, maxspeed = 10000000000, minspeed = 0):
        if time <= 0:
            self.setPos(x, y)
        else:
            time = self._MovementGetTimeMod(time)
            oldx, oldy = self.pos
            xdistance = x - oldx
            ydistance = y - oldy
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
            self.moveOverTime(time, xspeed, yspeed)
            self._move_to_point_end = [x,y]

    def moveToRelativePoint(self, time, x, y, *args, **kwargs):
        self.moveToPoint(time, x + self.pos[0], y + self.pos[1], *args, **kwargs)

    def finishMovement(self, useless_dt = None):
        self.stopMovement()
        if self._move_to_point_end != None:
            self.setPos(*self._move_to_point_end)
            self._move_to_point_end = None

    def runMovement(self):
        if not self.checkMovementPaused():
            time_passed = self._MovementGetTimePassed()
            newx = self.getPos()[0] + self.velocity[0]*time_passed + .5*self.acceleration[0]*time_passed
            newy = self.getPos()[1] + self.velocity[1]*time_passed + .5*self.acceleration[1]*time_passed
            self.setPos(newx, newy)
            self._setVelocity(self.velocity[0] + self.acceleration[0]*time_passed, self.velocity[1] + self.acceleration[1]*time_passed)

    def stopMovement(self):
        self._setVelocity(0,0)
        self._setAcceleration(0,0)

    def pauseMovement(self, key = MI_PAUSE_KEY):
        self._pause_movement.add(key)

    def unpauseMovement(self, key = MI_PAUSE_KEY):
        self._pause_movement.discard(key)

    def checkMovementPaused(self):
        return bool(self._pause_movement) or self.sleeping

    def setVelocity(self, *args, **kwargs):
        self._unscheduleEvents()
        self.schedule(self.runMovement, 0, repeat = True)
        self._setVelocity(*args, **kwargs)

    def _setVelocity(self, x = None, y = None):
        if x is None: x = self.velocity[0]
        if y is None: y = self.velocity[1]
        self.velocity = (float(x),float(y))
        self._updateMoving()

    def setAcceleration(self, *args, **kwargs):
        self._unscheduleEvents()
        self.schedule(self.runMovement, 0, repeat = True)
        self._setAcceleration(*args, **kwargs)

    def _setAcceleration(self, x = None, y = None):
        if x is None: x = self.acceleration[0]
        if y is None: y = self.acceleration[1]
        self.acceleration = (float(x),float(y))
        self._updateMoving()

    def getVelocity(self):
        return self.velocity

    def getAcceleration(self):
        return self.acceleration

    def checkMoving(self):
        return not (self.velocity[0] == 0 and self.velocity[1] == 0 and self.acceleration[0] == 0 and self.acceleration[1] == 0)

    def _updateMoving(self):
        if not self.checkMoving():
            self.unschedule(self.runMovement)

    def _unscheduleEvents(self):
        self.unschedule(self.runMovement)
        self.unscheduleMovementEvent(self.finishMovement)


    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        self._unscheduleEvents()

class MovementInterfaceFrames(MovementInterfaceBase):

    def __init__(self, *args, **kwargs):
        super(MovementInterfaceFrames, self).__init__(*args, **kwargs)
        self.scheduleMovementEvent = self.schedule
        self.unscheduleMovementEvent = self.unschedule

    def _MovementGetTimePassed(self):
        return 1.0/settings.getValue(DYNAMIC_SETTINGS_FRAMES_PER_SECOND)

    def _MovementGetWaitTime(self, time):
        return int(time * settings.getValue(DYNAMIC_SETTINGS_FRAMES_PER_SECOND))

    def _MovementGetTimeMod(self, time):
        return float(time) / settings.getValue(DYNAMIC_SETTINGS_FRAMES_PER_SECOND)


class MovementInterfaceRealtime(MovementInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(MovementInterfaceRealtime, self),__init__(*args, **kwargs)
        self.scheduleMovementEvent = self.scheduleRealtime
        self.unscheduleMovementEvent = self.unscheduleRealtime

    def _MovementGetTimePassed(self):
        return getRealtimeSinceLastFrame()

    def _MovementGetWaitTime(self, time):
        return time

    def _MovementGetTimeMod(self, time):
        return time
