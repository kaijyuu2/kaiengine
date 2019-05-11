

from .position_interface import PositionInterface
from .sleep_interface import SleepInterface

from kaiengine.gconfig import *
from kaiengine.resource import toStringPath, toListPath, combineStringPaths
from kaiengine.display import createGraphic, createGlowSprite

GI_SLEEP_KEY = "_GRAPHIC_INTERFACE_SLEEP_KEY"

class GraphicInterface(PositionInterface, SleepInterface):

    vars()[GPATH] = None
    vars()[GRAPHIC_INTERFACE_GLOWABLE] = False

    def __init__(self, sprite_path = None, *args, **kwargs):
        super(GraphicInterface, self).__init__(*args, **kwargs)
        self.sprite = None
        self._sprite_listener_keys = []
        self.setSpriteDefaults()
        if sprite_path:
            self.setSprite(sprite_path)

    def addSpriteFlagListener(self, anikey, listener, *args, **kwargs):
        self._sprite_listener_keys.append((self.sprite.addAniFlagListener(anikey, listener,*args, **kwargs), listener))

    def addSpriteTimeListener(self, anikey, listener, *args, **kwargs):
        self._sprite_listener_keys.append((self.sprite.addAniTimeListener(anikey, listener,*args, **kwargs), listener))

    def addSpriteFrameListener(self, anikey, listener, *args, **kwargs):
        self._sprite_listener_keys.append((self.sprite.addAniFrameListener(anikey, listener,*args, **kwargs), listener))

    def removeSpriteFlagListener(self, anikey, listener, *args, **kwargs):
        if self.sprite is not None:
            key = self.sprite.removeAniFlagListener(anikey, listener,*args, **kwargs)
            try: self._sprite_listener_keys.remove((key, listener))
            except ValueError: pass

    def removeSpriteTimeListener(self, anikey, listener, *args, **kwargs):
        if self.sprite is not None:
            key = self.sprite.removeAniTimeListener(anikey, listener,*args, **kwargs)
            try: self._sprite_listener_keys.remove((key, listener))
            except ValueError: pass

    def removeSpriteFrameListener(self, anikey, listener, *args, **kwargs):
        if self.sprite is not None:
            key = self.sprite.removeAniFrameListener(anikey, listener,*args, **kwargs)
            try: self._sprite_listener_keys.remove((key, listener))
            except ValueError: pass

    def removeAllSpriteListeners(self):
        if self.sprite is not None:
            for key, listener in self._sprite_listener_keys:
                self.sprite.removeAniListener(key, listener)
        self._sprite_listener_keys = []

    def setGraphicPath(self, newpath):
        """pass a path in list format to update it"""
        self._gpath = toListPath(newpath)

    def setSpriteDefaults(self):
        self._layer = 0
        self._center = [False,False]
        self._flip = [False,False]
        self._main_offset = [0,0]
        self._offsets = {}
        self._color = [1.0,1.0,1.0]
        self._alpha = 1.0
        self._size = [1.0,1.0]
        self._dimensions = None
        self._show = True
        self._tiled = False
        self._follow_camera = False

    def setPos(self, *args, **kwargs):
        super(GraphicInterface, self).setPos(*args, **kwargs)
        self._updateSpritePos()

    def setSprite(self, newspritepath, reset_properties = False):
        if newspritepath is not None and newspritepath != "":
            try: newspritepath[0] #check if already a sprite
            except:
                newsprite = newspritepath
            else:
                newspritepath = self.getGraphicPath(newspritepath)
                if not self._glowable:
                    newsprite = createGraphic(newspritepath)
                else:
                    newsprite = createGlowSprite(newspritepath)
            self.setSpriteDirect(newsprite, reset_properties)
        else:
            self.removeSpriteKeepProp()

    def setSpriteDirect(self, newsprite, reset_properties = False):
        self.removeAllSpriteListeners()
        if reset_properties:
            self.removeSprite()
        else:
            self.removeSpriteKeepProp()
        self.sprite = newsprite
        try:
            if self.sprite.default_center is not None:
                self._center = self.sprite.default_center[:]
        except AttributeError: pass
        try:
            if self.sprite.default_offset is not None:
                self._main_offset = self.sprite.default_offset[:]
        except AttributeError: pass
        try:
            if self.sprite.default_offsets is not None:
                self._offsets.update(self.sprite._offsets)
        except AttributeError: pass
        self._updateSprite()

    def getSpriteImagePath(self):
        if self.sprite:
            return self.sprite.getImagePath()
        return None

    def setSpriteAnimation(self, *args, **kwargs):
        try:
            self.sprite.set_animation(*args, **kwargs)
        except AttributeError:
            pass

    def checkSpriteAnimationFinished(self):
        try:
            return self.sprite.checkAnimationFinished()
        except AttributeError:
            return True

    def pauseSpriteAnimations(self, *args, **kwargs):
        try:
            self.sprite.pauseAnimations(*args, **kwargs)
        except AttributeError:
            pass

    def unpauseSpriteAnimations(self, *args, **kwargs):
        try:
            self.sprite.unpauseAnimations(*args, **kwargs)
        except AttributeError:
            pass

    def setSpriteAnimationSpeed(self, *args, **kwargs):
        try:
            self.sprite.setAnimationSpeed(*args, **kwargs)
        except AttributeError:
            pass


    def setSpriteColor(self, r = None, g = None, b = None, a_unused = None):
        '''color setter. Alpha value ignored; use setSpriteAlpha for that.'''
        if r == None: r = self._color[0]
        if g == None: g = self._color[1]
        if b == None: b = self._color[2]
        self._color = [r,g,b]
        self._updateSprite()


    def setSpriteAlpha(self, a):
        self._alpha = a
        self._updateSprite()

    def setSpriteLayer(self, layer):
        self._layer = layer
        self._updateSpriteLayer()

    def setSpriteCenter(self, x = None, y = None):
        if x is None:
            x = self._center[0]
        if y is None:
            y = self._center[1]
        self._center = [x,y]
        self._updateSprite()

    def setSpriteFlip(self, x = None, y = None):
        if x is None: x = self._flip[0]
        if y is None: y = self._flip[1]
        self._flip = [x,y]
        self._updateSprite()

    def setSpriteOffset(self, x = None, y = None):
        if x is None:
            x = self._main_offset[0]
        if y is None:
            y = self._main_offset[1]
        self._main_offset = [x,y]
        self._updateSprite()

    def setSpriteOtherOffset(self, offset_key, x = None, y = None):
        if x is None:
            try:
                x = self._offsets[offset_key][0]
            except KeyError:
                x = 0
        if y is None:
            try:
                y = self._offsets[offset_key][1]
            except KeyError:
                y = 0
        self._offsets[offset_key] = (x,y)
        self._updateSprite()

    def getSpriteOtherOffset(self, offset_key):
        try:
            return self._offsets[offset_key]
        except KeyError:
            return (0,0)

    def setSpriteShow(self, val):
        if self._show != val:
            self._show = val
            self._updateSpriteShow()

    def getSpriteShow(self):
        return self._show

    def setSpriteSize(self, x = None, y = None):
        if x is None: x = self._size[0]
        if y is None: y = self._size[1]
        if (x,y) != self._size:
            self._size = (x,y)
            self._updateSprite()

    def setSpriteFollowCamera(self, val):
        if self._follow_camera != val:
            self._follow_camera = val
            self._updateSprite()

    def checkSpriteOffscreen(self, *args, **kwargs):
        if self.sprite:
            return self.sprite.checkOffscreen(*args, **kwargs)
        return True

    def setSpriteDimensions(self, x = None, y = None):
        if self._dimensions == None:
            if x == None: x = 1
            if y == None: y = 1
        else:
            if x == None: x = self._dimensions[0]
            if y == None: y = self._dimensions[1]
        self._dimensions = (x,y)
        self._updateDimensions()
        
    def setSpriteWidth(self, newval):
        self.setSpriteDimensions(newval)
        
    def setSpriteHeight(self, newval):
        self.setSpriteDimensions(y=newval)

    def tileSprite(self, val = None):
        if val is None:
            self._tiled = not self._tiled
        else:
            self._tiled = val
        self._updateDimensions()

    def setSpriteTexDimensions(self, left = None, right = None, bottom = None, top = None):
        if self.sprite:
            if left == None: left = self.sprite.tex_widths[0]
            if right == None: right = self.sprite.tex_widths[1]
            if bottom == None: bottom = self.sprite.tex_heights[0]
            if top == None: top = self.sprite.tex_heights[1]
            self.sprite.set_texture_dimensions(left,right,bottom,top)

    def getSpriteTexDimensions(self):
        if self.sprite:
            return self.sprite.tex_widths + self.sprite.tex_heights
        return [0.0,1.0,0.0,1.0]


    def removeSpriteOtherOffset(self, offset_key):
        if offset_key in list(self._offsets.keys()):
            self._offsets.pop(offset_key)
            if self.sprite: #one of the few things not done in updatesprite
                self.sprite.remove_offset(offset_key)


    def removeSprite(self):
        self.removeSpriteKeepProp()
        self.setSpriteDefaults()

    def removeSpriteKeepProp(self):
        if self.sprite is not None:
            self.sprite.destroy()
            self.sprite = None

    def getSprite(self):
        #try not to use this
        return self.sprite

    def getGraphicPath(self, filename):
        '''return a formated graphic path in string format'''
        if self._gpath:
            return combineStringPaths(toStringPath(self._gpath), toStringPath(filename))
        return filename

    def getSpriteScreenPosition(self, *args, **kwargs):
        return self.sprite.getScreenPosition(*args, **kwargs)

    def getSpriteCenter(self):
        try: return self.sprite.center[:]
        except AttributeError: return [False,False]

    def getSpriteGraphicalCenter(self):
        return self.sprite.getCenterPosition()

    def getSpriteLayer(self):
        return self._layer

    def getSpriteFlip(self):
        return self._flip[:]

    def getSpriteWidth(self):
        if self._dimensions != None:
            return self._dimensions[0]
        if self.sprite:
            return self.sprite.getWidth()
        return 0

    def getSpriteHeight(self):
        if self._dimensions != None:
            return self._dimensions[1]
        if self.sprite:
            return self.sprite.getHeight()
        return 0

    def getSpriteColor(self):
        return self._color[:]

    def getSpriteAlpha(self):
        return self._alpha

    def getSpriteDimensions(self):
        if self._dimensions != None:
            return self._dimensions
        if self.sprite:
            return self.sprite.getDimensions()
        return (0,0)
    
    def resetDimensions(self):
        self._dimensions = None
    
    def getSpriteExtents(self):
        if self.sprite:
            return self.sprite.getExtents()
        return self._getDefaultExtents()
    
    def getSpriteExtentsMinusCamera(self):
        if self.sprite:
            return self.sprite.getExtentsMinusCamera()
        return self._getDefaultExtents()
    
    def _getDefaultExtents(self):
        pos = self.getPos()
        dimensions = self.getSpriteDimensions()
        return (pos[0], pos[0] + dimensions[0], pos[1], pos[1] + dimensions[1])

    def getSpriteLeftSide(self):
        extents = self.getSpriteExtentsMinusCamera()
        return (extents[0], (extents[2] + extents[3])/2)

    def getSpriteRightSide(self):
        extents = self.getSpriteExtentsMinusCamera()
        return (extents[1], (extents[2] + extents[3])/2)

    def getSpriteTopSide(self):
        extents = self.getSpriteExtentsMinusCamera()
        return ((extents[0] + extents[1])/2, extents[3])

    def getSpriteBottomSide(self):
        extents = self.getSpriteExtentsMinusCamera()
        return ((extents[0] + extents[1])/2, extents[2])
    
    def getBottomLeftCorner(self):
        extents = self.getSpriteExtentsMinusCamera()
        return (extents[0], extents[2])

    def _updateSprite(self):
        if self.sprite:
            self._updateSpritePos()
            self._updateSpriteLayer()
            self.sprite.setSize(*self._size)
            self.sprite.setCenter(*self._center)
            self.sprite.setFlip(*self._flip)
            self.sprite.setOffset(*self._main_offset)
            for key, offset in list(self._offsets.items()):
                self.sprite.change_offset(key, *offset)
            self.sprite.setColor(*self._color)
            self.sprite.alpha = self._alpha
            self._updateDimensions()
            self._updateSpriteShow()
            self.sprite.follow_camera = self._follow_camera

    def _updateSpritePos(self): #split from update for efficiency reasons
        try: self.sprite.setPos(*self.getPos())
        except AttributeError: pass

    def _updateSpriteLayer(self): #split from update for efficiency reasons
        try: self.sprite.layer = self._layer
        except AttributeError: pass

    def _updateDimensions(self):
        try:
            try: self.sprite.setDimensions(*self._dimensions)
            except TypeError: pass
            if self._tiled:
                self.sprite.tileTexture()
        except AttributeError:
            pass

    def _updateSpriteShow(self):
        try: self.sprite.show = False if self.sleeping else self._show
        except AttributeError: pass


    #overwritten stuff

    def sleep(self, *args, **kwargs):
        started_sleeping = super().sleep(*args, **kwargs)
        if started_sleeping:
            self.pauseSpriteAnimations(GI_SLEEP_KEY)
            self._updateSpriteShow()
        return started_sleeping

    def wakeUp(self, *args, **kwargs):
        awoken = super().wakeUp(*args, **kwargs)
        if awoken:
            self.unpauseSpriteAnimations(GI_SLEEP_KEY)
            self._updateSpriteShow()
        return awoken

    def destroy(self):
        super().destroy()
        self.removeAllSpriteListeners()
        self.removeSprite()
