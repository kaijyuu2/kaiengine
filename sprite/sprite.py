
import os
import copy
import math
import operator

from kaiengine import load
from kaiengine import timer
from kaiengine import sDict
from kaiengine import sGraphics
from kaiengine import camera
from kaiengine import settings
from kaiengine.timer import FrameTimer, checkCurrentFrame, scheduleRealtime, unscheduleRealtime, schedule, unschedule
from kaiengine.propertygetter import PropertyGetter
from kaiengine.uidgen import IdentifiedObject
from kaiengine.debug import debugHasKeyMessage, debugMessage
from kaiengine.resource import toStringPath, getInvalidGraphicPath, ResourceUnavailableError
from kaiengine.objectdestroyederror import ObjectDestroyedError
from kaiengine.event import customEvent, addCustomListener, removeCustomListener
from kaiengine.sset import SSet

from kaiengine.gconfig import *



#sprites

DEFAULT_ANI_PAUSE_KEY = "_DEFAULT_ANI_PAUSE"
SPRITE_SHOW_ANI_PAUSE_KEY = "_SHOW_FLAG_ANI_PAUSE"

DEFAULT_ANIMATION_FRAMES = [[[0,0,0,0],1.0]]

#x/y indexes
Xi = 0
Yi = 1



class Sprite(IdentifiedObject, sGraphics.sSprite):

    #default attributes
    vars()[SPRITE_ANIMATION_TYPE] = TIME_ANIMATION
    vars()[SPRITE_SHEET_TYPE] = SHEET_PROPORTIONAL
    vars()[SPRITE_ROWS] = 1
    vars()[SPRITE_COLUMNS] = 1
    vars()[SPRITE_STARTING_ANI] = None
    vars()[SPRITE_DEFAULT_ANI] = None
    vars()[SPRITE_DEFAULT_CENTER] = None #should be a list with x center and y center. ex: [True, False]
    vars()[SPRITE_DEFAULT_OFFSET] = None #should be a list with x offset and y offset ex: [100,0]
    vars()[SPRITE_DEFAULT_OFFSETS] = None #should be a list of lists with index name, x offset and y offset. ex: [["Test", 50, 50], ["hat", 100,0]]

    def __init__(self, img, layer = None, antialiasing = None, show = True):
        self._prop = {} #properties for loaded animations
        self._follow_camera = False
        self._camera_index = None
        self.gridsize = [1,1]
        self.image= [0,0] #goes from bottom left
        self.animations = {}
        self.current_ani = None
        self.starting_ani = None
        self.animation_speed = 1.0
        self._last_animation_speed = self.animation_speed
        self._pause_keys = set()
        self.animation_ticks = 0.0
        self._ani_opacity = 1.0
        self.default_ani = ANIMATION_DEFAULT
        self.ani_timer = timer.Timer()
        self.frame_ani_timer = FrameTimer()
        self.hard_fade_flag = False
        self.hard_fade_timer = timer.Timer()
        self._fade_opacity = 1.0
        self.time_listeners = {}
        self.frame_listeners = {}
        self.flag_events = {}
        self.flag_event_flags = {}
        self._anikeys = []
        self.last_ani_num = -1
        self.total_ani_time = 0.0
        self.last_ani_time = 0.0
        self.animation_finished = True
        try:
            super(Sprite, self).__init__(img)
        except ResourceUnavailableError:
            self.set_image(getInvalidGraphicPath())
        if layer is not None:
            self.layer = layer
        self.show = show

    @property
    def ani_opacity(self):
        return self._ani_opacity

    @ani_opacity.setter
    def ani_opacity(self, newval):
        self._ani_opacity = newval
        self.update_opacity()

    @property
    def fade_opacity(self):
        return self._fade_opacity

    @fade_opacity.setter
    def fade_opacity(self, newval):
        self._fade_opacity = newval
        self.update_opacity()

    @property
    def follow_camera(self):
        return self._follow_camera
    @follow_camera.setter
    def follow_camera(self, val):
        self.setFollowCamera(val)

    @property
    def bottom_left_corner(self):
        """returns the bottom left corner of the sprite, no matter where that might be"""
        effective_size = self.get_effective_size()
        width = self.width * effective_size[Xi]
        height = self.height * effective_size[Yi]
        if self.center[Xi]:
            center_xoffset = width / 2
        else:
            center_xoffset = 0
        if self.center[Yi]:
            center_yoffset = height / 2
        else:
            center_yoffset = 0
        xoffset = self.offset[Xi] * effective_size[Xi]
        yoffset = self.offset[Yi] * effective_size[Yi]
        for key, offset in self.other_offsets.items():
            if key != CAMERA_KEY:
                xoffset += offset[Xi]
                yoffset += offset[Yi]
        return (self.pos[Xi] + xoffset - center_xoffset, self.pos[Yi] + yoffset - center_yoffset)

    def setFollowCamera(self, val):
        if val:
            if not self._follow_camera:
                try:
                    self._camera_index = camera.addCameraSprite(self)
                except TypeError:
                    pass
                self.forceUpdateWithCamera()
        else:
            self.removeCameraSprite()
            self.stopUpdatingWithCamera()
        self._follow_camera = val

    def removeCameraSprite(self):
        try:
            camera.removeCameraSprite(self._camera_index)
        except TypeError:
            pass


    def _set_image_init(self, img = None):
        self.gridsize = [1,1]
        self.animations = {}
        self.current_ani = None
        self.starting_ani = None
        self.ani_timer.stopTimer()
        self.frame_ani_timer.stopTimer()
        self.last_ani_num = -1
        self.total_ani_time = 0.0
        if img is not None:
            self.add_animation(os.path.splitext(img)[0] + ".ani")
            if self.starting_ani:
                self.set_animation(self.starting_ani)
            elif SPRITE_DEFAULT_ANI_KEY in self.animations:
                self.starting_ani = SPRITE_DEFAULT_ANI_KEY
                self.set_animation(self.starting_ani)
            if self.follow_camera:
                self.forceUpdateWithCamera()


    def change_image(self, img, changeshow = None):
        #pass a list in [x,y] fashion to get the image number (proportial)
        #pass a list in [x,width,y,height] fasion to get the image window (absolute)
        self.image = img
        self.update_grid_texture()
        if changeshow is not None:
            self.show = changeshow

    def set_pixel_border(self): #set one pixel border. Don't call multiple times
        self.set_texture_dimensions(self.tex_widths[0] + 1, self.tex_widths[1] - 1, self.tex_heights[0] + 1, self.tex_heights[1] - 1)
        self.setDimensions(self.width -2, self.height -2)

    def update_grid_texture(self):
        if self.sheet_type == SHEET_PROPORTIONAL:
            xLength = self.original_width / self.gridsize[Xi]
            yLength = self.original_height / self.gridsize[Yi]
            self.set_texture_dimensions(xLength * self.image[Xi], xLength * (self.image[Xi] + 1),
                                yLength * self.image[Yi], yLength * (self.image[Yi] + 1))
        else:
            if len(self.image) < 4: #default behavior if accidentally using the other type
                self.image = [self.image[0], self.original_width / self.gridsize[Xi], self.image[1], self.original_height / self.gridsize[Yi]]
            self.set_texture_dimensions(self.image[0], self.image[0] + self.image[1], self.image[2], self.image[2] + self.image[3])
            self.width = self.image[1] #have to update these since the size may vary
            self.height = self.image[3]

    def setAnimationSpeed(self, newspeed):
        self._last_animation_speed = newspeed
        if not self.getAnimationPaused():
            self._SetAnimationSpeed(newspeed)

    def _SetAnimationSpeed(self, newspeed):
        if newspeed != self.animation_speed:
            #not the fastest way to do this but the easiest
            self.runAnimations()
            self.animation_speed = newspeed
            self.runAnimations()

    def getAnimationSpeed(self):
        return self._last_animation_speed

    def pauseAnimations(self, key = DEFAULT_ANI_PAUSE_KEY):
        self._pause_keys.add(key)
        self._SetAnimationSpeed(0)

    def unpauseAnimations(self, key = DEFAULT_ANI_PAUSE_KEY):
        self._pause_keys.discard(key)
        if not self.getAnimationPaused():
            self._SetAnimationSpeed(self._last_animation_speed)

    def forceUnpauseAnimations(self):
        self._pause_keys.clear()
        self._SetAnimationSpeed(self._last_animation_speed)

    def getAnimationPaused(self):
        return self._pause_keys

    def set_gridsize(self, x = None, y = None, reset_dim = False):
        if x is None:
            x = self.gridsize[Xi]
        if y is None:
            y = self.gridsize[Yi]
        self.gridsize = [x,y]
        self.update_grid_texture()
        if reset_dim:
            if self.sheet_type == SHEET_PROPORTIONAL:
                width, height = self.get_texture_dimensions()
                self.width = width / x
                self.height = height/ y
            else:
                self.width = self.image[1]
                self.height = self.image[3]


    def add_animation(self, anipath):
        ani = load.load_ani(anipath)
        if len(ani) == 0:
            ani = load.load_ani(toStringPath(os.path.dirname(anipath), DEFAULT_FOLDER_ANI))
            if len(ani) == 0:
                return
        if SPRITE_PROP in ani:
            for key, val in ani[SPRITE_PROP].items():
                debugHasKeyMessage(self, key, anipath)
                default = getattr(self, key, None)
                setattr(type(self), key, PropertyGetter(key, default))
            self._prop = ani[SPRITE_PROP]
            self.set_gridsize(self.columns, self.rows, True)
            if self.default_center is not None:
                self.setCenter(*self.default_center)
            if self.default_offset is not None:
                self.setOffset(*self.default_offset)
            if self.default_offsets is not None:
                for offset in self.default_offsets:
                    self.change_offset(*offset)
            del ani[SPRITE_PROP]
        for anikey, animation in list(ani.items()):
            if SPRITE_ANIMATION_FRAMES in animation:
                if self.animation_type == TIME_ANIMATION:
                    for l in animation[SPRITE_ANIMATION_FRAMES]:
                        l[1] = float(l[1]) / 1000 #convert from milliseconds to seconds
            else:
                animation[SPRITE_ANIMATION_FRAMES] = copy.copy(DEFAULT_ANIMATION_FRAMES)
            if SPRITE_ANIMATION_REPEAT not in animation:
                animation[SPRITE_ANIMATION_REPEAT] = True
            if SPRITE_ANIMATION_FREEZE not in animation:
                animation[SPRITE_ANIMATION_FREEZE] = False
            if SPRITE_ANIMATION_NEXT not in animation:
                animation[SPRITE_ANIMATION_NEXT] = self.default_ani
            try:
                for flag in animation[SPRITE_ANIMATION_FLAGS]:
                    for flagname in flag[1]:
                        self.addAniFlag(anikey, flagname, flag[0])
            except KeyError:
                animation[SPRITE_ANIMATION_FLAGS] = []
        self.animations.update(ani)


    def set_animation_by_list(self, animations, reset = True, default = True):
        for animation in animations:
            if animation in self.animations:
                self.set_animation(animation, reset = reset, default = default)
                return # skip remainder
        if default: #if none of the animations worked, try the default animation if default is true
            self.set_animation(self.default_ani, reset = reset, default = False)

    def set_animation_default(self, *args, **kwargs):
        #deprecated. call set_animation with None as its first argument or nothing as its first argument
        self.set_animation(None, *args, **kwargs)

    def set_animation(self, *args, **kwargs):
        '''deprecated function name'''
        self.setAnimation(*args, **kwargs)

    def setAnimation(self, anikey = None, reset = True, default = None, starting_time = 0.0):
        if anikey is None:
            anikey = self.default_ani
        if anikey in self.animations:
            self._set_animation(anikey, reset, starting_time)
        else:
            errorstring = ""
            if default is None: #suppress printing this error if a default was defined
                errorstring = str(anikey) + " animation key not found. "
            if default is False: #passing a false will skip changing the animation at all
                return
            else:
                default = self.default_ani
            if default in self.animations:
                self._set_animation(default,reset, starting_time)
            else:
                errorstring += "Moreover, default key " + str(default) + " not found."
            if errorstring:
                debugMessage(errorstring)

    def _set_animation(self, anikey, reset, starting_time):
        if not reset and self.current_ani == anikey:
            return
        self.total_ani_time = 0.0
        self.last_ani_time = starting_time
        for l in self.animations[anikey][SPRITE_ANIMATION_FRAMES]:
            self.total_ani_time += l[1]
        self.current_ani = anikey
        self.ani_timer.start()
        self.frame_ani_timer.Start()
        self.animation_ticks = 0.0
        self.last_ani_num = -1
        self.set_ani_image(0)
        self.animation_finished = False
        self.runAnimations()

    def runAnimations(self, useless_arg = None):
        if self.current_ani is not None:
            if self.animation_type == TIME_ANIMATION:
                self.animation_ticks += float(self.ani_timer.Tick()) * self.animation_speed
            else:
                self.animation_ticks += float(self.frame_ani_timer.Tick()) * self.animation_speed
            aniticks_verification = self.animation_ticks #for checking if the animation was set to something different during an event
            aninum_verification = self.current_ani
            anitime = self.animation_ticks % self.total_ani_time
            aninum = 0
            for l in self.animations[self.current_ani][SPRITE_ANIMATION_FRAMES]:
                anitime -= l[1]
                if anitime < 0.0:
                    break
                aninum += 1
            overflows = int((self.animation_ticks - self.last_ani_time) / self.total_ani_time)
            #call listeners
            if overflows == 0:
                try: self.callTimeListeners(self.current_ani, self.time_listeners[self.current_ani][self.last_ani_time % self.total_ani_time : anitime])
                except KeyError: pass
                try: self.callFrameListeners(self.current_ani, self.frame_listeners[self.current_ani][self.last_ani_num+1 : aninum])
                except KeyError: pass
                try:
                    for flag in self.flag_event_flags[self.current_ani]:
                        try: self.callFlagListeners(self.current_ani, flag, self.flag_events[self.current_ani][flag][self.last_ani_num+1 : aninum])
                        except KeyError: pass
                except KeyError: pass
            else:
                try:
                    self.callTimeListeners(self.current_ani, self.time_listeners[self.current_ani][self.last_ani_time % self.total_ani_time : ])
                    for i in range(overflows-1):
                        self.callTimeListeners(self.current_ani, self.time_listeners[self.current_ani][ : ])
                    self.callTimeListeners(self.current_ani, self.time_listeners[self.current_ani][ : anitime])
                except KeyError: pass
                try:
                    self.callFrameListeners(self.current_ani, self.frame_listeners[self.current_ani][self.last_ani_num+1 : ])
                    for i in range(overflows-1):
                        self.callFrameListeners(self.current_ani, self.frame_listeners[self.current_ani][ : ])
                    self.callFrameListeners(self.current_ani, self.frame_listeners[self.current_ani][ : aninum])
                except KeyError: pass
                try:
                    for flag in self.flag_event_flags[self.current_ani]:
                        try:
                            self.callFlagListeners(self.current_ani, flag, self.flag_events[self.current_ani][flag][self.last_ani_num+1 : ])
                            for i in range(overflows-1):
                                self.callFlagListeners(self.current_ani, flag, self.flag_events[self.current_ani][flag][ : ])
                            self.callFlagListeners(self.current_ani, flag, self.flag_events[self.current_ani][flag][ : aninum])
                        except KeyError: pass
                except KeyError: pass
            if not (self.animation_ticks == aniticks_verification and self.current_ani == aninum_verification): #animation was modified during listeners; abort
                return
            if not self.animations[self.current_ani][SPRITE_ANIMATION_REPEAT]:
                if self.animation_ticks >= self.total_ani_time or self.animation_ticks <= -self.total_ani_time:
                    if not self.animations[self.current_ani][SPRITE_ANIMATION_FREEZE]:
                        self.set_animation(self.animations[self.current_ani][SPRITE_ANIMATION_NEXT])
                    else:
                        self.set_ani_image(len(self.animations[self.current_ani][SPRITE_ANIMATION_FRAMES])-1,0)
                        self.animationFinished()
                    return
            try: self.set_ani_image(aninum, overflows)
            except ObjectDestroyedError:
                self.stopAnimations()
            self.last_ani_time = self.animation_ticks
            try:
                if self.animation_type == TIME_ANIMATION:
                    unscheduleRealtime(self.runAnimations)
                    scheduleRealtime(self.runAnimations, -anitime / self.animation_speed)
                else:
                    unschedule(self.runAnimations)
                    schedule(self.runAnimations, -anitime / self.animation_speed)
            except ZeroDivisionError:
                pass

    def stopAnimations(self):
        self.current_ani = None
        unschedule(self.runAnimations)
        unscheduleRealtime(self.runAnimations)

    def animationFinished(self):
        self.animation_finished = True
        self.callFinishListeners(self.current_ani)

    def runHardFade(self):
        self.fade_opacity = self.hard_fade_timer.getCountdownPercent()
        if self.hard_fade_timer.checkCountdown():
            self.hard_fade_flag = False
            unschedule(self.runHardFade)


    def set_ani_image(self, num, number_of_frames_cycled = 0):
        if self.last_ani_num is not num:
            self.change_image(self.animations[self.current_ani][SPRITE_ANIMATION_FRAMES][num][0])
            self.last_ani_num = num


    def checkAnimationFinished(self):
        #only ever set to True if an animation that doesn't repeat and freezes at the end stops, or no animation was ever set at all
        return self.animation_finished

    def addAniFlag(self, anikey, flag, time):
        if anikey not in self.flag_events:
            self.flag_events[anikey] = {}
            self.flag_event_flags[anikey] = set()
        self.flag_event_flags[anikey].add(flag)
        try:
            self.flag_events[anikey][flag].add(time)
        except KeyError:
            self.flag_events[anikey][flag] = SSet()
            self.flag_events[anikey][flag].add(time)

    def addAniFlagListener(self, anikey, listener, flag):
        if anikey is None: anikey = self.current_ani
        key = self.generateAniKeyFlag(anikey, flag)
        self._registerAniListener(key, listener)
        return key

    def addAniTimeListener(self, anikey, listener, time):
        if anikey is None: anikey = self.current_ani
        key = self.generateAniKeyTime(anikey, time)
        self._registerAniListener(key, listener)
        try: self.time_listeners[anikey].add(time)
        except KeyError:
            self.time_listeners[anikey] = SSet()
            self.time_listeners[anikey].add(time)
        return key

    def addAniFrameListener(self, anikey, listener, frame):
        if anikey is None: anikey = self.current_ani
        key = self.generateAniKeyFrame(anikey, frame)
        self._registerAniListener(key, listener)
        try: self.frame_listeners[anikey].add(frame)
        except KeyError:
            self.frame_listeners[anikey] = SSet()
            self.frame_listeners[anikey].add(frame)
        return key

    def addAniFinishListener(self, anikey, listener):
        if anikey is None: anikey = self.current_ani
        key = self.generateAniKeyFinish(anikey)
        self._registerAniListener(key, listener)
        return key

    def _registerAniListener(self, key, listener):
        addCustomListener(key, listener)
        self._anikeys.append((key, listener))

    def removeAniFlagListener(self, anikey, listener, flag):
        return self.removeAniListener(self.generateAniKeyFlag(anikey, flag), listener)

    def removeAniTimeListener(self, anikey, listener, time):
        return self.removeAniListener(self.generateAniKeyTime(anikey, time), listener)

    def removeAniFrameListener(self, anikey, listener, frame):
        return self.removeAniListener(self.generateAniKeyFrame(anikey, frame), listener)

    def removeAniFinishListener(self, anikey, listener):
        return self.removeAniListener(self.generateAniKeyFinish(anikey), listener)

    def removeAniListener(self, key, listener):
        try: self._anikeys.remove((key, listener))
        except KeyError: pass
        removeCustomListener(key, listener)
        return key

    def removeAllListeners(self):
        for key, listener in self._anikeys:
            removeCustomListener(key, listener)
        self._anikeys = []

    def _getFlagFrameIndex(self, anikey, flag):
        frameindex = -1
        for flagdata in self.animations[anikey][SPRITE_ANIMATION_FLAGS]:
            if flag in flagdata[1]:
                frameindex = flagdata[0]
                break
        if frameindex == -1:
            raise KeyError("Flag doesn't exist")
        else:
            return frameindex

    def generateAniKeyFlag(self, anikey, flag):
        return self._generateAniKey(anikey, flag, "FLAG")

    def generateAniKeyTime(self, anikey, time):
        return self._generateAniKey(anikey, time, "TIME")

    def generateAniKeyFrame(self, anikey, frame):
        return self._generateAniKey(anikey, frame, "FRAME")

    def generateAniKeyFinish(self, anikey):
        return self._generateAniKey(anikey, 0, "FINISH")

    def _generateAniKey(self, anikey, time, extra):
        return self.id + str(anikey) + str(time) + str(extra)

    def callTimeListeners(self,anikey, times):
        for time in times:
            customEvent(self.generateAniKeyTime(anikey, time))

    def callFrameListeners(self, anikey, frames):
        for frame in frames:
            customEvent(self.generateAniKeyFrame(anikey, frame))

    def callFlagListeners(self, anikey, flag, frames):
        for frame in frames:
            customEvent(self.generateAniKeyFlag(anikey, flag))

    def callFinishListeners(self, anikey):
        customEvent(self.generateAniKeyFinish(anikey))

    def hard_fade(self, time):
        self.hard_fade_flag = True
        self.hard_fade_timer.countdownStart(time)
        unschedule(self.runHardFade)
        schedule(self.runHardFade, 0, repeat = True)

    def update_opacity(self):
        self.alpha = self.fade_opacity * self.ani_opacity
        
    def getExtentsMinusCamera(self):
        extents = list(self.getExtents())
        try:
            offset = self.other_offsets[CAMERA_KEY]
            extents[0] -= offset[0]
            extents[1] -= offset[0]
            extents[2] -= offset[1]
            extents[3] -= offset[1]
        except KeyError:
            pass
        return extents

    def getScreenPosition(self, centered = False):
        if centered:
            pos = self.getCenterPosition()
        else:
            pos = self.getPos()
            if self.follow_camera:
                pos = list(map(operator.sub, pos, camera.getCameraXY()))
        return pos

    def getCenterPosition(self):
        extents = self.getExtentsMinusCamera()
        return (extents[0] + extents[1])/2, (extents[2] + extents[3])/2

    def getLeftSide(self):
        """returns the left side of the sprite, no matter where that might be"""
        extents = self.getExtentsMinusCamera()
        return extents[0], (extents[2] + extents[3])/2

    def getRightSide(self):
        extents = self.getExtentsMinusCamera()
        return extents[1], (extents[2] + extents[3])/2

    def getBottomSide(self):
        extents = self.getExtentsMinusCamera()
        return (extents[0] + extents[1])/2, extents[2]

    def getTopSide(self):
        extents = self.getExtentsMinusCamera()
        return (extents[0] + extents[1])/2, extents[3]

    def getBottomLeftCorner(self):
        extents = self.getExtentsMinusCamera()
        return extents[0], extents[2]

    def forceUpdateWithCamera(self):
        self.updateWithCamera(*camera.getCameraXY())

    def updateWithCamera(self, x, y):
        self.change_offset(CAMERA_KEY, x, y) 

    def stopUpdatingWithCamera(self):
        self.remove_offset(CAMERA_KEY)

    def checkOffscreen(self, x_buffer = None, y_buffer = None):
        from kaiengine.display import getWindowDimensionsScaled
        if x_buffer is None: x_buffer = self.width
        if y_buffer is None: y_buffer = self.height
        x, y = self.getScreenPosition()
        return x < -x_buffer or y < -y_buffer or x > getWindowDimensionsScaled()[0] + x_buffer or y > getWindowDimensionsScaled()[1] + y_buffer

    #overwritten stuff


    def setShow(self, val):
        super().setShow(val)
        if self.show:
            self.unpauseAnimations(SPRITE_SHOW_ANI_PAUSE_KEY)
        else:
            self.pauseAnimations(SPRITE_SHOW_ANI_PAUSE_KEY)

    def set_image(self, img, *args, **kwargs):
        super(Sprite, self).set_image(img, *args, **kwargs)
        self._set_image_init(img)

    def set_image_from_buffer(self, name, *args, **kwargs):
        super(Sprite, self).set_image_from_buffer(name, *args, **kwargs)
        self._set_image_init()

    def destroy(self): #when destroyed:
        super().destroy()
        self.removeAllListeners()
        try:
            unscheduleRealtime(self.runAnimations)
            unschedule(self.runAnimations)
            unschedule(self.runHardFade)
        except:
            pass
            #if self.ani_thread_timer is not None:
            #    self.ani_thread_timer.cancel()
            #    self.ani_thread_timer = None
        self.removeCameraSprite()
