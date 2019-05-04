
from kaiengine.gconfig import *
import kaiengine.display as display
import kaiengine.graphicobject as graphicobject
from kaiengine.resource import toStringPath
from kaiengine.debug import debugMessage
import traceback, copy

BORDERED_POS_KEY = "BORDERED_POS_KEY"
BORDERED_CENTER_KEY = "BORDERED_CENTER_KEY"

TOP_LEFT_KEY = "borderUL"
TOP_KEY = "borderU"
TOP_RIGHT_KEY = "borderUR"
LEFT_KEY = "borderL"
CENTER_KEY = ""
RIGHT_KEY = "borderR"
BOTTOM_LEFT_KEY = "borderBL"
BOTTOM_KEY = "borderB"
BOTTOM_RIGHT_KEY = "borderBR"

SPRITE_NAMES = [TOP_LEFT_KEY, TOP_KEY, TOP_RIGHT_KEY, LEFT_KEY, CENTER_KEY,
            RIGHT_KEY, BOTTOM_LEFT_KEY, BOTTOM_KEY, BOTTOM_RIGHT_KEY]

TOP_LEFT = 0
TOP = 1
TOP_RIGHT = 2
LEFT = 3
CENTER = 4
RIGHT = 5
BOTTOM_LEFT = 6
BOTTOM = 7
BOTTOM_RIGHT = 8

class SpriteBordered(graphicobject.GraphicObject):

    vars()[EXTENSION] = BORDERED_SPRITE_EXTENSION

    def __init__(self,data, layer, tiled = True,*args, **kwargs):
        super(SpriteBordered, self).__init__(path = data, layer = layer, *args, **kwargs)
        self._width = 100
        self._height = 100
        self._gfx_path = data[FILEPATH][:]
        self._gfx_name = data[FILENAME]
        self.border_width = 0
        self.border_height = 0
        self._tiled = tiled
        self._offset = (0,0)

        self.add_graphic()

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, newvalue):
        if self._width != newvalue:
            self._width = newvalue
            self.update_dimensions()

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, newvalue):
        if self._height != newvalue:
            self._height = newvalue
            self.update_dimensions()

    @property
    def center(self):
        return self._center
    @center.setter
    def center(self, newvalue):
        if self._center != newvalue:
            self._center = newvalue
            self.update_dimensions()
    def update_center(self):
        pass #overwrite this

    @property
    def tiled(self):
        return self._tiled
    @tiled.setter
    def tiled(self, newvalue):
        if self._tiled != newvalue:
            self._tiled = newvalue
            self.update_dimensions()
            
    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, newvalue):
        self.setOffset(*newvalue)

    @property
    def other_offsets(self):
        try:
            offsets = copy.deepcopy(list(self.sprites.values())[0].other_offsets) #just get one of these
            offsets.pop(BORDERED_POS_KEY, None) #this is fairly shitty... reimplement with parent owning canon copy of offsets?
            offsets.pop(BORDERED_CENTER_KEY, None)
            return offsets
        except IndexError:
            return {}
    @other_offsets.setter
    def other_offsets(self, *args, **kwargs):
        debugMessage("Cannot set other_offsets directly")

    def setOffset(self, x = None, y = None): #TODO: make this not look glitchy
        x = x if x is not None else self._offset[0]
        y = y if y is not None else self._offset[1]
        self._offset = (x,y)
        for sprite in list(self.sprites.values()):
            sprite.setOffset(*self._offset)

    def setDimensions(self, x = None, y = None):
        if x is not None:
            self._width = x
        if y is not None:
            self._height = y
        self.update_dimensions()


    def add_graphic(self):
        self.remove_sprites()
        for name in SPRITE_NAMES:
            self.sprites.append(display.createGraphic(toStringPath(self._gfx_path + [self._gfx_name + name + PNG_EXTENSION]), self.layer))
        self.show = True
        self.update_dimensions()

    def setCenterSprite(self, sprite, tiled = None): #pass a premade sprite
        self.sprites[CENTER].destroy()
        self.sprites[CENTER] = sprite
        if tiled is not None:
            self._tiled = tiled
        self.update_dimensions()
        self.update_sprites()


    def setPos(self, *args, **kwargs):
        super(SpriteBordered, self).setPos(*args, **kwargs)
        try:
            self.sprites[0]
        except KeyError:
            pass
        else:
            self.update_dimensions()

    def update_dimensions(self):
        self.border_width = self.sprites[TOP_LEFT].original_width
        self.border_height = self.sprites[TOP_LEFT].original_height
        if self.width < self.border_width * 2:
            self.border_width = self.width / 2
        if self.height < self.border_height * 2:
            self.border_height = self.height / 2
        if self.border_width <= 0:
            self.border_width = 1
        if self.border_height <= 0:
            self.border_height = 1
        if self.center[0]:
            center_x_offset = -self.width / 2
        else:
            center_x_offset = 0
        if self.center[1]:
            center_y_offset = -self.height / 2
        else:
            center_y_offset = 0
        self.change_offset(BORDERED_CENTER_KEY, center_x_offset, center_y_offset)
        self.change_offset(BORDERED_POS_KEY, *self.pos)
        try:
            self.sprites[TOP_LEFT].pos = [0, self.height - self.border_height]
            self.sprites[TOP_LEFT].height = self.border_height
            self.sprites[TOP_LEFT].width = self.border_width
            self.sprites[TOP_LEFT].set_texture_dimensions(0.0, self.sprites[TOP_LEFT].width, self.sprites[TOP_LEFT].original_height - self.sprites[TOP_LEFT].height,self.sprites[TOP_LEFT].original_height)
            self.sprites[TOP].pos = [self.border_width, self.height - self.border_height]
            self.sprites[TOP].width = self.width - 2 * self.border_width
            self.sprites[TOP].height = self.border_height
            self.sprites[TOP].set_texture_dimensions(0.0, self.sprites[TOP].width, self.sprites[TOP].original_height - self.sprites[TOP].height,self.sprites[TOP].original_height)
            self.sprites[TOP_RIGHT].pos = [self.width - self.border_width, self.height - self.border_height]
            self.sprites[TOP_RIGHT].height = self.border_height
            self.sprites[TOP_RIGHT].width = self.border_width
            self.sprites[TOP_RIGHT].set_texture_dimensions(self.sprites[TOP_RIGHT].original_width - self.sprites[TOP_RIGHT].width, self.sprites[TOP_RIGHT].original_width, self.sprites[TOP_RIGHT].original_height - self.sprites[TOP_RIGHT].height,self.sprites[TOP_RIGHT].original_height)
            self.sprites[LEFT].pos = [0, self.border_height]
            self.sprites[LEFT].height = self.height - 2 * self.border_height
            self.sprites[LEFT].width = self.border_width
            self.sprites[LEFT].set_texture_dimensions(0.0, self.sprites[LEFT].width, 0.0, self.sprites[LEFT].height)
            self.sprites[CENTER].pos = [self.border_width, self.border_height]
            self.sprites[CENTER].height = self.height - 2 * self.border_height
            self.sprites[CENTER].width = self.width - 2 * self.border_width
            if self.tiled:
                self.sprites[CENTER].set_texture_dimensions(0.0, self.sprites[CENTER].width, 0.0, self.sprites[CENTER].height)
            else:
                self.sprites[CENTER].set_texture_dimensions(0.0, self.sprites[CENTER].original_width, 0.0, self.sprites[CENTER].original_height)
            self.sprites[RIGHT].pos = [self.width - self.border_width, self.border_height]
            self.sprites[RIGHT].height = self.height - 2 * self.border_height
            self.sprites[RIGHT].width = self.border_width
            self.sprites[RIGHT].set_texture_dimensions(0.0, self.sprites[RIGHT].width, 0.0, self.sprites[RIGHT].height)
            self.sprites[BOTTOM_LEFT].pos = [0,0]
            self.sprites[BOTTOM_LEFT].height = self.border_height
            self.sprites[BOTTOM_LEFT].width = self.border_width
            self.sprites[BOTTOM_LEFT].set_texture_dimensions(0.0, self.sprites[BOTTOM_LEFT].width, 0.0, self.sprites[BOTTOM_LEFT].height)
            self.sprites[BOTTOM].pos = [self.border_width,0]
            self.sprites[BOTTOM].width = self.width - 2 * self.border_width
            self.sprites[BOTTOM].height = self.border_height
            self.sprites[BOTTOM].set_texture_dimensions(self.sprites[BOTTOM].original_width - self.sprites[BOTTOM].width, self.sprites[BOTTOM].original_width, 0.0, self.sprites[BOTTOM].height)
            self.sprites[BOTTOM_RIGHT].pos = [self.width - self.border_width, 0]
            self.sprites[BOTTOM_RIGHT].height = self.border_height
            self.sprites[BOTTOM_RIGHT].width = self.border_width
            self.sprites[BOTTOM_RIGHT].set_texture_dimensions(self.sprites[BOTTOM_RIGHT].original_width - self.sprites[BOTTOM_RIGHT].width, self.sprites[BOTTOM_RIGHT].original_width, 0.0, self.sprites[BOTTOM_RIGHT].height)
        except Exception as e:
            debugMessage(traceback.format_exc())
            debugMessage(e)


    def get_border_width(self):
        return self.border_width

    def get_border_height(self):
        return self.border_height

    def get_border_dim(self):
        return [self.border_width,self.border_height]

    def getWidth(self):
        try:
            return self.width
        except:
            return 0

    def getHeight(self):
        try:
            return self.height
        except:
            return 0

    def remove_sprites(self):
        if SpriteBordered:
            super(SpriteBordered, self).remove_sprites()
        self.border_width = 0
        self.border_height = 0

    def getDimensions(self):
        return (self.getWidth(), self.getHeight())

    def getLeftSide(self):
        return self.sprites[LEFT].getLeftSide()

    def getRightSide(self):
        return self.sprites[RIGHT].getRightSide()

    def getTopSide(self):
        return self.sprites[TOP].getTopSide()

    def getBottomSide(self):
        return self.sprites[BOTTOM].getBottomSide()

    def getBottomLeftCorner(self):
        return self.sprites[BOTTOM_LEFT].getBottomLeftCorner()
