

'''very specific and very hardcoded graphic object for labels using graphic fonts'''

from kaiengine import camera
from kaiengine.gconfig import *
from kaiengine.graphicobject import GraphicObject
from kaiengine import fonts
from .label_base import Label_Base
from kaiengine.sDict import sDict
from kaiengine.fonts import FontTypeError

import os
import operator

class Label_Graphic(Label_Base, GraphicObject):
    def __init__(self, text = None, font_size = DEFAULT_TEXT_SIZE, font = DEFAULT_FONT, color = DEFAULT_TEXT_COLOR, layer = -1, show = True, *args, **kwargs):
        self._offset = [0,0]
        self._other_offsets = sDict()
        self._width_scalar = 1.0
        self._height_scalar = 1.0
        self._lazy_hidden_sprite = False
        self._camera_index = None
        self._font = font
        super(Label_Graphic, self).__init__(None, font_size, font, color, layer, *args, **kwargs)
        self.show = show
        if text is not None:
            self.set_text(text)

    @property
    def font(self):
        return self._font
    @font.setter
    def font(self, newvalue):
        if self.font_usable(newvalue):
            if newvalue != self._font:
                self._font = newvalue
                self._set_text()
        else:
            ext = os.path.splitext(newvalue)[1]
            raise FontTypeError("Wrong font extension: " + ext + ". Graphical fonts can only change to other graphical fonts")


    @property
    def size(self):
        multiplier = self.get_relative_font_size()
        return [self._size[0] * multiplier, self._size[1] * multiplier]
    @size.setter
    def size(self, value):
        self._size = value
        self.update_size()
    @property
    def font_size(self):
        return self._font_size
    @font_size.setter
    def font_size(self, value):
        self._font_size = value
        self.update_size()
    def get_relative_font_size(self):
        if self.font_size is not None and self.font is not None:
            return float(self.font_size) / fonts.getDefaultFontSize(self.font)
        else:
            return 1

    @property
    def original_width(self):
        total = 0
        for sprite in list(self.sprites.values()):
            total += sprite.original_width
        return total
    @property
    def original_height(self):
        for sprite in list(self.sprites.values()):
            return sprite.original_height
        return 0
    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, newvalue):
        if self._offset != newvalue:
            self._offset = newvalue
            self.update_offset()
    def update_offset(self):
        self.update_pos()

    @property
    def other_offsets(self):
        return self._other_offsets
    @other_offsets.setter
    def other_offsets(self, offsets):
        self._other_offsets = offsets
        self.update_other_offsets()
    def update_other_offsets(self): #note: doesn't remove offsets that might have different keys in the sub sprite
        for key, val in list(self._other_offsets.items()):
            for sprite in list(self.sprites.values()):
                sprite.change_offset(key, *val)

    @property
    def width(self):
        total = 0
        for sprite in list(self.sprites.values()):
            total += sprite.width
        return total
    @width.setter
    def width(self, newvalue):
        for sprite in list(self.sprites.values()):
            perc = float(sprite.original_width) / self.original_width
            sprite.width = int(perc * sprite.original_width)
        self.update_pos()
    @property
    def height(self):
        for sprite in list(self.sprites.values()):
            return sprite.height
        return 0
    @height.setter
    def height(self, newvalue):
        for sprite in list(self.sprites.values()):
            sprite.height = newvalue

    def update_flip(self):
        self._update_flip()
        self.update_pos()

    def _update_flip(self):
        for sprite in list(self.sprites.values()):
            sprite.flip = self.flip

    def update_center(self):
        self.update_pos()

    def update_show(self):
        super(Label_Graphic, self).update_show()
        if self._lazy_hidden_sprite and self.show:
            self._lazy_hidden_sprite = False
            self._set_text()

    @property
    def follow_camera(self):
        return self._follow_camera
    @follow_camera.setter
    def follow_camera(self, val):
        if val:
            if not self._follow_camera:
                try:
                    self._camera_index = camera.addCameraSprite(self)
                except TypeError:
                    pass
                self.forceUpdateWithCamera()
        else:
            try:
                camera.removeCameraSprite(self._camera_index)
            except TypeError:
                pass
            self.stopUpdatingWithCamera()
        self._follow_camera = val

    def update_follow_camera(self):
        pass

    @property
    def bottom_left_corner(self):
        """returns the bottom left corner of the sprite, no matter where that might be"""
        if len(self.sprites) == 0:
            return self.pos[:]
        return self.sprites[0].bottom_left_corner

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, newvalue):
        if self._pos != newvalue:
            self._offsetPos(self._pos, newvalue)
            self._pos = newvalue
    def _offsetPos(self, oldpos, newpos):
        #faster than update_pos if we're just changing position
        offset = list(map(operator.sub, newpos, oldpos))
        for sprite in list(self.sprites.values()):
            spritepos = sprite.pos
            sprite.setPos(spritepos[0] + offset[0], spritepos[1] + offset[1])

    def update_pos(self):
        if self.center[1]:
            y_offset = self.height / 2
        else:
            y_offset = 0
        if self.center[0]:
            x_offset = self.width / 2
        else:
            x_offset = 0
        totalwidth = 0
        for key in sorted(list(self.sprites.keys()), reverse=True) if self.flip[0] else list(self.sprites.keys()):
            self.sprites[key].setPos(self.pos[0], self.pos[1])
            self.sprites[key].offset = [float(totalwidth - x_offset + self.offset[0]) * self._width_scalar,float(-y_offset + self.offset[1]) * self._height_scalar]
            totalwidth += self.sprites[key].width

    def getPos(self):
        return self._pos


    def set_text(self, text, font_size = None, font = None, color = None):
        if font_size is None:
            if self.font_size is None:
                self.font_size = DEFAULT_TEXT_SIZE
        else:
            self.font_size = font_size
        if color is None:
            if self.color is None:
                self.color = DEFAULT_TEXT_COLOR
        else:
            self.color = color
        if text != self.text:
            self.text = text
            self._set_text()

    def _set_text(self):
        if self.text is not None:
            if self.show:
                self.remove_sprites()
                for sprite in fonts.getSpriteList(self.text, self.font, self.font_size):
                    self.add_sprite(sprite)
                self.update_sprites()
            else:
                self._lazy_hidden_sprite = True

    def remove_text(self):
        self.remove_sprites()
        self.text = None
        self.font_size = DEFAULT_GRAPHICAL_FONT_SIZE
        self.color = DEFAULT_TEXT_COLOR
        self._width_scalar = 1.0
        self._height_scalar = 1.0


    def setFontSize(self, newsize):
        self.font_size = newsize
        self._set_text()

    def set_font_size(self, *args, **kwargs):
        """deprected form of setFontSize"""
        self.setFontSize(*args, **kwargs)

    def set_font_color(self, color):
        self.color = color

    def setFont(self, new_font):
        self.font = new_font
        self._set_text()

    def set_font(self, *args, **kwargs):
        """deprecated form of setFont"""
        self.setFont(*args, **kwargs)

    def font_usable(self, new_font):
        return os.path.splitext(new_font)[1] == GRAPHIC_FONT_EXTENSION

    def setOffset(self, x = None, y = None):
        if x is None:
            x = self._offset[0]
        if y is None:
            y = self._offset[1]
        self.offset = [x,y]

    def append_offset(self, x = 0, y = 0):
        self.other_offsets.append([x,y])
        self.update_other_offsets()

    def remove_offset(self, index):
        if index in list(self.other_offsets.keys()):
            del self.other_offsets[index]
        for sprite in list(self.sprites.values()):
            sprite.remove_offset(index)

    def change_offset(self, index, x = None, y = None):
        if index not in list(self.other_offsets.keys()):
            tempoffset = [0,0]
        else:
            tempoffset = self.other_offsets[index]
        if x is None:
            x = tempoffset[0]
        if y is None:
            y = tempoffset[1]
        self.other_offsets[index] = [x, y]
        self.update_other_offsets()


    def set_dimensions(self, x = None, y = None):
        if x is None: x = self.width
        if y is None: y = self.height
        if x != self.width or y != self.height:
            try:
                self._width_scalar = float(x) / self.width
            except ZeroDivisionError:
                self._width_scalar = 1.0
            try:
                self._height_scalar = float(y) / self.height
            except ZeroDivisionError:
                self._height_scalar = 1.0
            for sprite in list(self.sprites.values()):
                sprite.width = float(sprite.original_width) * self._width_scalar
                sprite.height = float(sprite.original_height) * self._height_scalar
            self.update_sprites()



    def update_sprites(self):
        self.update_layer()
        self.update_size()
        self.update_color()
        self.update_alpha()
        self._update_flip()
        self.update_follow_camera()
        self.update_pos()

    def getLeftSide(self):
        """returns the left side of the sprite, no matter where that might be"""
        if len(self.sprites) == 0:
            return self.pos[:]
        return getLeftSide(self.sprites[0])

    def getRightSide(self, *args, **kwargs):
        return self.getRightSide(*args, **kwargs)

    def getRightSide(self):
        if len(self.sprites) == 0:
            return self.pos[:]
        return getRightSide(self.sprites.last_item())

    def getTopSide(self, *args, **kwargs):
        return self.getTopSide(*args, **kwargs)

    def getTopSide(self):
        if len(self.sprites) == 0:
            return self.pos[:]
        pos = getTopSide(self.sprites[0])
        x = self.pos[0]
        effective_width = self.size[0] * self.width
        if not self.center[0]:
            x += effective_width/2
        return (x,pos[1])

    def getBottomSide(self, *args, **kwargs):
        return self.getBottomSide(*args, **kwargs)

    def getBottomSide(self):
        if len(self.sprites) == 0:
            return self.pos[:]
        return (self.getTopSide()[0], getBottomSide(self.sprites[0])[1])

    def getBottomLeftCorner(self):
        if len(self.sprites) == 0:
            return self.pos[:]
        return getBottomLeftCorner(self.sprites[0])


    def forceUpdateWithCamera(self):
        self.updateWithCamera(*camera.getCameraXY())

    def updateWithCamera(self, x, y):
        for sprite in list(self.sprites.values()):
            sprite.change_offset(CAMERA_KEY, x, y)#rounding fixes jittering when scrolling

    def stopUpdatingWithCamera(self):
        for sprite in list(self.sprites.values()):
            sprite.remove_offset(CAMERA_KEY)
            
    def getScreenPosition(self):
        if self.follow_camera:
            return self.getPos()
        else:
            return list(map(operator.sub, self.getPos(), camera.getCameraXY()))

#recreated functions

Xi = 0
Yi = 1

def getLeftSide(sprite):
    """returns the left side of the sprite, no matter where that might be"""
    effective_size = sprite.get_effective_size()
    width = sprite.width * effective_size[Xi]
    height = sprite.height * effective_size[Yi]
    if sprite.center[Xi]:
        center_xoffset = width / 2
    else:
        center_xoffset = 0
    if sprite.center[Yi]:
        center_yoffset = height / 2
    else:
        center_yoffset = 0
    xoffset = sprite.offset[Xi] * effective_size[Xi]
    yoffset = sprite.offset[Yi] * effective_size[Yi]
    for offset in list(sprite.other_offsets.values()):
        xoffset += offset[Xi]
        yoffset += offset[Yi]
    return (sprite.pos[Xi] + xoffset - center_xoffset, sprite.pos[Yi] + yoffset - center_yoffset + height/2)

def getRightSide(sprite):
    pos = getLeftSide(sprite)
    return (pos[0] + sprite.width * sprite.get_effective_size()[0], pos[1])

def getBottomSide(sprite):
    effective_size = sprite.get_effective_size()
    width = sprite.width * effective_size[Xi]
    height = sprite.height * effective_size[Yi]
    if sprite.center[Xi]:
        center_xoffset = width / 2
    else:
        center_xoffset = 0
    if sprite.center[Yi]:
        center_yoffset = height / 2
    else:
        center_yoffset = 0
    xoffset = sprite.offset[Xi] * effective_size[Xi]
    yoffset = sprite.offset[Yi] * effective_size[Yi]
    for offset in list(sprite.other_offsets.values()):
        xoffset += offset[Xi]
        yoffset += offset[Yi]
    return (sprite.pos[Xi] + xoffset - center_xoffset + width/2, sprite.pos[Yi] + yoffset - center_yoffset)

def getTopSide(sprite):
    pos = getBottomSide(sprite)
    return (pos[0], pos[1] + sprite.height * sprite.get_effective_size()[1])

def getBottomLeftCorner(sprite):
    effective_size = sprite.get_effective_size()
    width = sprite.width * effective_size[Xi]
    height = sprite.height * effective_size[Yi]
    if sprite.center[Xi]:
        center_xoffset = width / 2
    else:
        center_xoffset = 0
    if sprite.center[Yi]:
        center_yoffset = height / 2
    else:
        center_yoffset = 0
    xoffset = sprite.offset[Xi] * effective_size[Xi]
    yoffset = sprite.offset[Yi] * effective_size[Yi]
    for offset in list(sprite.other_offsets.values()):
        xoffset += offset[Xi]
        yoffset += offset[Yi]
    return (sprite.pos[Xi] + xoffset - center_xoffset, sprite.pos[Yi] + yoffset - center_yoffset)
