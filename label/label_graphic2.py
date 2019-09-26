

'''used for ttfs and other non-graphic fonts that create a dynamic texture'''

import os, operator

from kaiengine import sGraphics
from kaiengine import fonts
from kaiengine import camera
from kaiengine.objectdestroyederror import ObjectDestroyedError

from kaiengine.gconfig import *

from .label_base import Label_Base

Xi = 0
Yi = 1


class LabelGraphic2(Label_Base, sGraphics.sSprite):
    def __init__(self, text = None, font_size = MENU_TEXT_SIZE, font = DEFAULT_FONT, color = DEFAULT_TEXT_COLOR, layer = -1, show = True, bordered=False):
        self._follow_camera = False
        self._camera_index = None
        super(LabelGraphic2, self).__init__(None, font_size, font, color, layer, bordered)
        self.show = show
        if text is not None:
            self.set_text(text)

    @property
    def follow_camera(self):
        return self._follow_camera
    @follow_camera.setter
    def follow_camera(self, val):
        if val:
            if not self._follow_camera:
                self._camera_index = camera.addCameraSprite(self)
                self.forceUpdateWithCamera()
        else:
            camera.removeCameraSprite(self._camera_index)
            self.stopUpdatingWithCamera()
        self._follow_camera = val

    @property
    def bottom_left_corner(self):
        """returns the bottom left corner of the sprite, no matter where that might be"""
        return self.getBottomLeftCorner()

    @property
    def font(self):
        return self._font
    @font.setter
    def font(self, newvalue):
        if self.font_usable(newvalue):
            if fonts is not None: #end of game error suppression
                self._font = fonts.getFontPath(newvalue)
        else:
            raise fonts.FontTypeError("fonts other than gfont2/3 aren't supported for graphic font 2 label objects")

    def setText(self, text, font_size = None, font = None, color = None):
        self.text = text
        if font_size is None:
            if self.font_size is None:
                self.font_size = MENU_TEXT_SIZE
        else:
            self.font_size = font_size
        if font is None:
            if self.font is None:
                self.font = DEFAULT_FONT
        else:
            self.font = font
        if color is None:
            if self.color is None:
                self.color = DEFAULT_TEXT_COLOR
        else:
            self.color = NormalizeColorFormat(color)
        self._set_text()

    set_text = setText #deprecated function name

    def _set_text(self):
        if self.text is not None:
            self.set_image(fonts.textToImage(self.text, font_path = self.font))
            self._setPixelBorder()
            if self.follow_camera:
                self.forceUpdateWithCamera()

    def remove_text(self):
        try:
            self.remove_image()
            self.text = None
            try: self.font = DEFAULT_FONT
            except fonts.FontTypeError: pass
            self.font_size = MENU_TEXT_SIZE
            self.color = DEFAULT_TEXT_COLOR
            self.bordered = False
        except ObjectDestroyedError:
            pass

    def setFontSize(self, newsize):
        self.font_size = newsize
        self._set_text()

    def set_font_size(self, *args, **kwargs):
        """deprected form of setFontSize"""
        self.setFontSize(*args, **kwargs)

    def set_font_color(self, color):
        self.color = NormalizeColorFormat(color)

    def setFont(self, new_font):
        self.font = new_font
        self._set_text()

    def set_font(self, *args, **kwargs):
        """deprecated form of setFont"""
        self.setFont(*args, **kwargs)

    def font_usable(self, newvalue):
        try:
            extension = os.path.splitext(newvalue)[1]
            return extension == GRAPHIC_FONT_2_EXTENSION or extension == GRAPHIC_FONT_3_EXTENSION
        except AttributeError: #end of game error suppression
            return True

    def getScreenPosition(self, centered = False):
        if centered:
            pos = self.getCenterPosition()
        else:
            pos = self.getPos()
        if self.follow_camera:
            return pos
        else:
            return list(map(operator.sub, pos, camera.getCameraXY()))

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

    def getCenterPosition(self):
        """returns the center of the sprite, no matter where that might be"""
        extents = self.getExtentsMinusCamera()
        return (extents[0] + extents[1])/2, (extents[2] + extents[3])/2

    def getLeftSide(self):
        """returns the left side of the sprite, no matter where that might be"""
        extents = self.getExtentsMinusCamera()
        return extents[0], (extents[2] + extents[3])/2

    def getRightSide(self):
        """returns the right side of the sprite, no matter where that might be"""
        extents = self.getExtentsMinusCamera()
        return extents[1], (extents[2] + extents[3])/2

    def getTopSide(self):
        """returns the Top side of the sprite, no matter where that might be"""
        extents = self.getExtentsMinusCamera()
        return (extents[0] + extents[1])/2,  extents[3]

    def getBottomSide(self):
        """returns the bottom side of the sprite, no matter where that might be"""
        extents = self.getExtentsMinusCamera()
        return (extents[0] + extents[1])/2,  extents[2]

    def getBottomLeftCorner(self):
        """returns the bottom left corner of the sprite, no matter where that might be"""
        extents = self.getExtentsMinusCamera()
        return extents[0], extents[2]

    def forceUpdateWithCamera(self):
        self.updateWithCamera(*camera.getCameraXY())

    def updateWithCamera(self, x, y):
        self.change_offset(CAMERA_KEY, x, y)

    def stopUpdatingWithCamera(self):
        try:
            self.remove_offset(CAMERA_KEY)
        except ObjectDestroyedError:
            pass

    def getScreenPosition(self):
        if self.follow_camera:
            return self.getPos()
        else:
            return list(map(operator.sub, self.getPos(), camera.getCameraXY()))

    def _setPixelBorder(self): #set one pixel border. Don't call multiple times
        self.set_texture_dimensions(self.tex_widths[0] + 1, self.tex_widths[1] - 1, self.tex_heights[0] + 1, self.tex_heights[1] - 1)
        self.setDimensions(self.width -2, self.height -2)

    def destroy(self):
        if LabelGraphic2 is not None: #end of game error suppression:
            super(LabelGraphic2, self).destroy()
        if camera: #game close error suppression
            self.follow_camera = False
        self.remove_text()
