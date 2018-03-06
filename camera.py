
from . import timer
import operator
import weakref
from . import display
import math
from . import sBool
from .sDict import sDict
from . import sGraphics
from kaiengine.debug import debugMessage
from kaiengine.gconfig import *

#camera class & driver

CameraObj = None

def initCamera():
    global CameraObj
    CameraObj = camera()

def getCameraMoving():
    return CameraObj.get_moving()

def getCameraX():
    return CameraObj.getX()

def getCameraY():
    return CameraObj.getY()

def getCameraXY():
    return [getCameraX(), getCameraY()]

def setCameraCenterXY(x, y):
    CameraObj.center(x, y)

def setCameraXY(x, y):
    CameraObj.set_x(x)
    CameraObj.set_y(y)

def moveCameraOverTime(pos, time, **kwargs):
    CameraObj.move_over_time(pos, time, **kwargs)

def setXBoundaries(x, x2):
    CameraObj.set_x_boundary(x, x2)

def setYBoundaries(y, y2):
    CameraObj.set_y_boundary(y, y2)

def setBoundaries(x, x2, y, y2):
    setXBoundaries(x, x2)
    setYBoundaries(y, y2)

def setCameraOffset(*args, **kwargs):
    CameraObj.setOffset(*args, **kwargs)

def getCameraOffset(*args, **kwargs):
    return CameraObj.getOffset(*args, **kwargs)

def clearCameraOffset(*args, **kwargs):
    CameraObj.clearOffset(*args, **kwargs)

def setScrollBuffer(val):
    CameraObj.set_scroll_buffer(val)

def setUseScrollBuffer(val):
    CameraObj.set_use_scroll_buffer(val)

def setUseCameraBoundary(val):
    CameraObj.set_use_camera_boundary(val)

def setAllowMovement(val, reset = None):
    CameraObj.set_allow_movement(val, reset)

def getAllowMovement():
    return CameraObj.get_allow_movement()

def lockToScreen():
    CameraObj.lock_to_screen_dim()

def moveX(dx):
    CameraObj.move_x(dx)

def moveY(dy):
    CameraObj.move_y(dy)

def moveXY(dx, dy):
    moveX(dx)
    moveY(dy)

def addCameraSprite(sprite):
    return CameraObj.addCameraSprite(sprite)

def removeCameraSprite(index):
    CameraObj.removeCameraSprite(index)

def runCamera():
    CameraObj.run()

def updateCameraSprites():
    CameraObj.updateCameraSprites()

def updateInternalCamera():
    CameraObj.update_internal_camera()

DEFAULT_CAMERA_OFFSET_KEY = "_DEFAULT_CAMERA_OFFSET_KEY"

class camera(object):
    def __init__(self):
        self._x = 0
        self._y = 0
        self.boundary_x = [0,1]
        self.boundary_y = [0,1]
        self.timer = timer.Timer()
        self.startpos = [0,0]
        self.endpos = [0,0]
        self.use_scroll_buffer = False
        self.use_camera_boundary = False
        self.scroll_buffer = CAMERA_SCROLL_BUFFER
        self.allow_camera_movement = sBool.sBool(force = False)
        self.camera_sprites = sDict()
        self._oldx = self._x
        self._oldy = self._y
        self.camera_offsets = {}

    @property
    def x(self):
        return self.getX()
    @x.setter
    def x(self, val):
        self.set_x(float(val))
    @property
    def y(self):
        return self.getY()
    @y.setter
    def y(self, val):
        self.set_y(float(val))

    def run(self):
        self.run_movement()

    def run_movement(self):
        if self.timer.started:
            perc = 1.0 - self.timer.getCountdownPercent()
            distance_total = list(map(operator.sub, self.endpos, self.startpos))
            distance_current = list(map(operator.mul, distance_total, [perc,perc]))
            pos = list(map(operator.add, distance_current, self.startpos))
            self.set_x(int(pos[0]))
            self.set_y(int(pos[1]))
            if perc >= 1:
                self.timer.stopTimer()

    def move_over_time(self, endpos, pixels_per_second = 600, mintime = .01, maxtime = 1.0, center = True):
        if center:
            endpos = list(map(operator.sub, endpos, list(map(operator.floordiv, display.getWindowDimensionsScaled(), [2,2]))))
        self.startpos = [self.x, self.y]
        self.endpos = endpos
        pos_difference = list(map(operator.sub, endpos, self.startpos))
        distance_direct = math.sqrt(math.pow(pos_difference[0],2) + math.pow(pos_difference[1], 2))
        time = distance_direct/ pixels_per_second
        if maxtime < time:
            time = maxtime
        elif mintime > time:
            time = mintime
        self.timer.countdownStart(time)

    def move_x(self, x):
        self.set_x(self.getX() + x)

    def move_y(self, y):
        self.set_y(self.getY() + y)

    def lock_to_screen_dim(self):
        self.set_x_boundary(0, display.getWindowDimensionsScaled()[0])
        self.set_y_boundary(0, display.getWindowDimensionsScaled()[1])
        self.set_use_scroll_buffer(False)
        self.set_x(0)
        self.set_y(0)

    def center(self, x, y):
        windowsize = display.getWindowDimensionsScaled()
        newx = x - (windowsize[0] / 2)
        newy = y - (windowsize[1] / 2)
        self.set_x(newx)
        self.set_y(newy)

    def set_x(self, x):
        if self.use_camera_boundary:
            if self.use_scroll_buffer:
                scroll_buffer = self.scroll_buffer
            else:
                scroll_buffer = 0
            lower_boundary = self.boundary_x[0] - scroll_buffer
            if x < lower_boundary:
                x = lower_boundary
            upper_boundary = self.boundary_x[1] - display.getWindowDimensionsScaled()[0] + scroll_buffer
            if x >= upper_boundary:
                x = upper_boundary -1
        self._x = x

    def set_y(self, y):
        if self.use_camera_boundary:
            if self.use_scroll_buffer:
                scroll_buffer = self.scroll_buffer
            else:
                scroll_buffer = 0
            lower_boundary = self.boundary_y[0] - scroll_buffer
            if y < lower_boundary:
                y = lower_boundary
            upper_boundary = self.boundary_y[1] - display.getWindowDimensionsScaled()[1] + scroll_buffer
            if y >= upper_boundary:
                y = upper_boundary - 1
        self._y = y

    def set_x_boundary(self, x, x2):
        self.boundary_x = (x, x2)

    def set_y_boundary(self, y, y2):
        self.boundary_y = (y, y2)

    def setOffset(self, key = None, x = None, y = None):
        if key is None: key = DEFAULT_CAMERA_OFFSET_KEY
        if x is None: x = self.camera_offsets.get(key, [0,0])[0]
        if y is None: y = self.camera_offsets.get(key, [0,0])[1]
        self.camera_offsets[key] = (x,y)

    def getOffset(self, key = None):
        if key is None: key = DEFAULT_CAMERA_OFFSET_KEY
        return self.camera_offsets.get(key, (0,0))

    def clearOffset(self, key):
        try: del self.camera_offsets[key]
        except KeyError: pass

    def getX(self):
        #gets corrected camera position for drawing objects
        offset = 0
        for cam_offset in self.camera_offsets.values():
            offset += cam_offset[0]
        return self._x + offset

    def getY(self):
        #gets corrected camera position for drawing objects
        offset = 0
        for cam_offset in self.camera_offsets.values():
            offset += cam_offset[1]
        return self._y + offset

    def set_scroll_buffer(self, val, allow = None):
        self.scroll_buffer = val
        if allow is not None:
            self.set_use_scroll_buffer(allow)

    def set_use_scroll_buffer(self, val):
        self.use_scroll_buffer = val

    def set_use_camera_boundary(self, val):
        self.use_camera_boundary = val

    def get_moving(self):
        return self.timer.started

    def set_allow_movement(self, val, reset = None):
        if reset is not None:
            self.allow_camera_movement.reset(val)
        else:
            self.allow_camera_movement.set(val)

    def get_allow_movement(self):
        return self.allow_camera_movement.check()

    def addCameraSprite(self, sprite):
        self.camera_sprites.append(weakref.ref(sprite))
        return self.camera_sprites.last_key()

    def removeCameraSprite(self, index):
        try:
            del self.camera_sprites[index]
        except:
            pass

    def update_internal_camera(self):
        """updates with the graphics engine's camera"""
        sGraphics.setCameraXY(self.x, self.y) #rounded so global scaling doesn't cause half pixel movements and the like

    def updateCameraSprites(self):
        x = self.getX()
        y = self.getY()
        if self._oldx != x or self._oldy != y:
            for key, sprite in list(self.camera_sprites.items()): #cast to list so we can remove keys if there's an exception
                try:
                    sprite().updateWithCamera(x,y)
                    #method(sprite(), x, y)
                except Exception as e:
                    debugMessage(e)
                    debugMessage("Camera sprite update function broke. Removed object that was following the camera? deleting")
                    self.removeCameraSprite(key)
            self._oldx = x
            self._oldy = y


