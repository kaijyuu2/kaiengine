from .baseobject import BaseObject
from .sDict import sDict
from .uidgen import IdentifiedObject
from .sGraphics import RED, GREEN, BLUE #import color constants
from .debug import debugMessage
from . import display
from .gconfig import *


#anything that draws graphics but isn't a sprite or label object


#x/y indexes
Xi = 0
Yi = 1

DEFAULT_SIZE_KEY = "_GRAPHIC_OBJECT_DEFAULT_SIZE_KEY"


class GraphicObject(BaseObject, IdentifiedObject):

    #base prop
    vars()[EXTENSION] = GRAPHIC_OBJECT_EXTENSION
    vars()[PATH] = FULL_GRAPHIC_OBJECTS_PATH

    def __init__(self, path = None, layer = -1, show = True, *args, **kwargs):
        self._pos = [0,0]
        self._layer = layer
        self._size = sDict()
        self._size[DEFAULT_SIZE_KEY] = [1.0, 1.0]
        self._color = [1.0,1.0,1.0]
        self._alpha = 1.0
        self._show = show
        self._center = [False,False]
        self._flip = [False,False]
        self._follow_camera = False

        self.sprites = sDict()

        super(GraphicObject, self).__init__(path, *args, **kwargs)


    @property
    def image_path(self):
        debugMessage("image_path function not defined for " + self.getFilename())
        return 0
    @image_path.setter
    def image_path(self, newvalue):
        debugMessage("image_path is read-only")

    @property
    def original_width(self):
        debugMessage("original_width function not defined for " + self.getFilename())
        return 0
    @original_width.setter
    def original_width(self, newvalue):
        debugMessage("original_width is read-only")

    @property
    def original_height(self):
        debugMessage("original_height function not defined for " + self.getFilename())
        return 0
    @original_height.setter
    def original_height(self, newvalue):
        debugMessage("original_height is read-only")

    @property
    def update_image(self):
        debugMessage("update_image function not defined for " + self.getFilename())
        return False
    @update_image.setter
    def update_image(self, newvalue):
        for sprite in self.sprites.values():
            sprite.update_image = newvalue

    @property
    def layer(self):
        return self._layer
    @layer.setter
    def layer(self, newvalue):
        self._layer = newvalue
        self.update_layer()
    def update_layer(self):
        for sprite in self.sprites.values():
            sprite.layer = self.layer

    @property
    def pos(self):
        return self.getPos()
    @pos.setter
    def pos(self, newvalue):
        if self._pos != newvalue:
            self.setPos(*newvalue)

    @property
    def offset(self):
        debugMessage("offset function not defined for " + self.getFilename())
        return [0,0]
    @offset.setter
    def offset(self, newvalue):
        debugMessage("offset setter function not defined for " + self.getFilename())

    @property
    def other_offsets(self):
        debugMessage("other_offsets function not defined for " + self.getFilename())
        return sDict()
    @other_offsets.setter
    def other_offsets(self, newvalue):
        debugMessage("other_offsets setter function not defined for " + self.getFilename())

    @property
    def width(self):
        debugMessage("width function not defined for " + self.getFilename())
        return 0
    @width.setter
    def width(self, newvalue):
        debugMessage("width setter function not defined for " + self.getFilename())

    @property
    def height(self):
        debugMessage("height function not defined for " + self.getFilename())
        return 0
    @height.setter
    def height(self, newvalue):
        debugMessage("height setter function not defined for " + self.getFilename())

    @property
    def tex_widths(self):
        debugMessage("tex_widths function not defined for " + self.getFilename())
        return [0,0]
    @tex_widths.setter
    def tex_widths(self, newvalue):
        debugMessage("tex_widths setter function not defined for " + self.getFilename())

    @property
    def tex_heights(self):
        debugMessage("tex_heights function not defined for " + self.getFilename())
        return [0,0]
    @tex_heights.setter
    def tex_heights(self, newvalue):
        debugMessage("tex_heights setter function not defined for " + self.getFilename())

    @property
    def size(self):
        return self.getSize()
    @size.setter
    def size(self, *args, **kwargs):
        self.setSize(*args, **kwargs)
        
    def update_size(self):
        for sprite in self.sprites.values():
            sprite.size = self.size

    @property
    def color(self):
        return self._color[:3]
    @color.setter
    def color(self, newvalue):
        self._color = newvalue
        self.update_color()
    def update_color(self):
        for sprite in self.sprites.values():
            sprite.color = self.color

    @property
    def alpha(self):
        return self._alpha
    @alpha.setter
    def alpha(self, newvalue):
        self._alpha = newvalue
        self.update_alpha()
    def update_alpha(self):
        for sprite in self.sprites.values():
            sprite.alpha = self.alpha

    @property
    def show(self):
        return self._show
    @show.setter
    def show(self, newvalue):
        self._show = newvalue
        self.update_show()
    def update_show(self):
        for sprite in self.sprites.values():
            sprite.show = self.show

    @property
    def center(self):
        return self._center
    @center.setter
    def center(self, newvalue):
        if self._center != newvalue:
            self._center = newvalue
            self.update_center()
    def update_center(self):
        for sprite in self.sprites.values():
            sprite.center = self.center

    @property
    def flip(self):
        return self._flip
    @flip.setter
    def flip(self, newvalue):
        if self._flip != newvalue:
            self._flip = newvalue
            self.update_flip()
    def update_flip(self):
        for sprite in self.sprites.values():
            sprite.flip = self.flip

    @property
    def follow_camera(self):
        return self._follow_camera
    @follow_camera.setter
    def follow_camera(self, newvalue):
        self._follow_camera = newvalue
        self.update_follow_camera()
    def update_follow_camera(self):
        for sprite in self.sprites.values():
            sprite.follow_camera = self.follow_camera

    @property
    def bottom_left_corner(self):
        """returns the bottom left corner of the sprite, no matter where that might be"""
        debugMessage("bottom_left_corner not defined for " + self.getFilename())
        return self.pos[:]


    def setPos(self, x = None, y = None):
        try:
            x[0]
        except:
            pass
        else:
            x, y = x
        if x is None:
            x = self.pos[Xi]
        if y is None:
            y = self.pos[Yi]
        self._pos = (x,y)

    def getPos(self):
        return self._pos
    
    def setOffset(self, x = None, y = None):
        debugMessage("setOffset function not defined for " + self.getFilename())

    def append_offset(self, *args, **kwargs):
        for sprite in self.sprites.values():
            sprite.append_offset(*args, **kwargs)

    def remove_offset(self, *args, **kwargs):
        for sprite in self.sprites.values():
            sprite.remove_offset(*args, **kwargs)

    def change_offset(self, *args, **kwargs):
        for sprite in self.sprites.values():
            sprite.change_offset(*args, **kwargs)

    def setDimensions(self, *args, **kwargs):
        debugMessage("setDimensions function not defined for " + self.getFilename())

    def set_texture_dimensions(self, xLeft = None, xRight = None, yBottom = None, yTop = None):
        debugMessage("set_texture_dimensions function not defined for " + self.getFilename())
        
    def getSize(self, key = DEFAULT_SIZE_KEY):
        return self._size.get(key, (1.0,1.0))

    def setSize(self, x = None, y = None, key = DEFAULT_SIZE_KEY):
        if x is None:
            x = self.getSize(key)[Xi]
        if y is None:
            y = self.getSize(key)[Yi]
        self._size[key] = (x,y)
        
    def get_effective_size(self):
        returnval = [1.0,1.0]
        for size in self._size.values():
            returnval[Xi] *= size[Xi]
            returnval[Yi] *= size[Yi]
        return returnval

    def setColor(self, r = None, g = None, b = None, alpha = None):
        #alpha setting is completely ignored
        if r is None:
            r = self.color[RED]
        if g is None:
            g = self.color[GREEN]
        if b is None:
            b = self.color[BLUE]
        self.color = [r,g,b]


    def setCenter(self, x = None, y = None):
        if x is None:
            x = self.center[Xi]
        if y is None:
            y = self.center[Yi]
        self.center = [x,y]

    def setFlip(self, x = None, y = None):
        if x is None:
            x = self.flip[Xi]
        if y is None:
            y = self.flip[Yi]
        self.flip = [x,y]

    def set_image(self, image_path, tex_id = None, keep_dim = True, display = True):
        debugMessage("set_image function not defined for " + self.getFilename())

    def set_image_from_buffer(self, image_name, ix, iy, image_buffer, keep_dim = True, display = True):
        debugMessage("set_image_from_buffer function not defined for " + self.getFilename())

    def remove_image(self, keep_dim = True):
        debugMessage("remove_image function not defined for " + self.getFilename())


    def get_dimensions(self):
        try:
            return self.width, self.height
        except:
            debugMessage("width and/or height not defined for " + self.getFilename())
            return [0,0]

    def get_effective_dimensions(self):
        try:
            return self.width * self.size[0], self.height * self.size[0]
        except:
            debugMessage("effective width and/or height not defined for " + self.getFilename())
            return [0,0]
        
    def getExtents(self):
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
        xleft = self.pos[Xi] + xoffset - center_xoffset
        xright = self.pos[Xi] + xoffset - center_xoffset + width
        ybottom = self.pos[Yi] + yoffset - center_yoffset
        ytop = self.pos[Yi] + yoffset - center_yoffset + height
        for key, offset in self.other_offsets.items():
            try:
                xleft += offset[Xi]
                xright += offset[Xi]
                ybottom += offset[Yi]
                ytop += offset[Yi]
            except TypeError:
                debugMessage("error with graphical offset. Key: " + key)
                self.other_offsets[key] = [0,0]
        return xleft, xright, ybottom, ytop

        
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
            return pos
        else:
            return list(map(operator.sub, pos, camera.getCameraXY()))

        
    def getCenterPosition(self):
        """returns the center of the sprite, no matter where that might be"""
        if not self.sprites:
            return self.pos[:]
        else:
            return (self.getTopSide()[0], self.getLeftSide()[1])
        
    def getLeftSide(self):
        """returns the left side of the sprite, no matter where that might be"""
        debugMessage("getLeftSide not defined for " + self.getFilename())
        return self.pos[:]

    def getRightSide(self):
        """returns the right side of the sprite, no matter where that might be"""
        debugMessage("getRightSide not defined for " + self.getFilename())
        return self.pos[:]

    def getTopSide(self):
        """returns the Top side of the sprite, no matter where that might be"""
        debugMessage("getTopSide not defined for " + self.getFilename())
        return self.pos[:]

    def getBottomSide(self):
        """returns the bottom side of the sprite, no matter where that might be"""
        debugMessage("getBottomSide not defined for " + self.getFilename())
        return self.pos[:]

    def getBottomLeftCorner(self):
        """returns the bottom left corner of the sprite, no matter where that might be"""
        debugMessage("getBottomLeftCorner not defined for " + self.getFilename())
        return self.pos[:]

    def add_sprite(self, sprite, key = None):
        try: #check if this is a path or a pre-created sprite
            sprite[0]
        except:
            pass
        else:
            sprite = display.createGraphic(sprite)
        if key is None:
            key = self.sprites.append(sprite)
        else:
            self.remove_sprite(key)
            self.sprites[key] = sprite
        #self.update_sprites()
        return key

    def remove_sprite(self, key = None):
        if key == None:
            try: key = sorted(self.sprites.keys())[0]
            except IndexError: return
        try:
            self.sprites[key].destroy()
            del self.sprites[key]
        except KeyError:
            pass

    def remove_sprites(self):
        for sprite_key in list(self.sprites.keys()):
            self.sprites[sprite_key].destroy()
            del self.sprites[sprite_key]
        self.sprites.clear()

    def update_sprites(self):
        self.update_layer()
        self.update_size()
        self.update_color()
        self.update_alpha()
        self.update_center()
        self.update_flip()
        self.update_follow_camera()
        self.update_show()

    def destroy(self):
        if GraphicObject: #end of game error suppression:
            super(GraphicObject, self).destroy()
        self.remove_sprites()
