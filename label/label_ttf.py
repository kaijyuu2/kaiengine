

'''used for ttfs and other non-graphic fonts that create a dynamic texture'''

from kaiengine import sGraphics
from kaiengine import fonts
import os
from kaiengine import camera
from kaiengine.gconfig import *
from .label_base import Label_Base
from kaiengine.objectdestroyederror import ObjectDestroyedError

Xi = 0
Yi = 1


class Label_TTF(Label_Base, sGraphics.sSprite):
    def __init__(self, text = None, font_size = MENU_TEXT_SIZE, font = DEFAULT_FONT, color = DEFAULT_TEXT_COLOR, layer = -1, show = True, bordered=False):
        self._bordered = None
        self._follow_camera = False
        self._camera_index = None
        super(Label_TTF, self).__init__(text, font_size, font, color, layer, bordered)
        self.show = show
        if self.text is not None:
            self.set_text(text)


    @property
    def bordered(self):
        return self._bordered
    @bordered.setter
    def bordered(self, val):
        if self._bordered != val:
            self._bordered = val
            self._set_text() #regenerate texture

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
        for key, offset in list(self.other_offsets.items()):
            if key != CAMERA_KEY:
                xoffset += offset[Xi]
                yoffset += offset[Yi]
        return (self.pos[Xi] + xoffset - center_xoffset, self.pos[Yi] + yoffset - center_yoffset)

    @property
    def font(self):
        return self._font
    @font.setter
    def font(self, newvalue):
        if self.font_usable(newvalue):
            if fonts is not None: #end of game error suppression
                self._font = fonts.getFontPath(newvalue)
        else:
            raise fonts.FontTypeError("fonts other than ttf aren't supported for textlabel objects")

    def setFollowCamera(self, val):
        if val:
            if not self._follow_camera:
                self._camera_index = camera.addCameraSprite(self)
                self.forceUpdateWithCamera()
        else:
            try: #end of game error suppression
                camera.removeCameraSprite(self._camera_index)
            except TypeError:
                pass
            self.stopUpdatingWithCamera()
        self._follow_camera = val

    def set_text(self, text, font_size = None, font = None, color = None):
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

    def _set_text(self):
        if self.text is not None:
            self.set_image_from_buffer(None,*fonts.textToImageBuffer(self.text, self.font_size, self.font, self.bordered))
            if self.follow_camera:
                self.forceUpdateWithCamera()

    def remove_text(self):
        try:
            self.remove_image()
            self.text = None
            self.font = DEFAULT_FONT
            self.font_size = MENU_TEXT_SIZE
            self.color = DEFAULT_TEXT_COLOR
            self.bordered = False
        except (ObjectDestroyedError, TypeError): #type error is game close error suppression
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
            return extension == TTF_EXTENSION
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

    def getCenterPosition(self):
        effsize = self.get_effective_size()
        xoffset = 0
        yoffset = 0
        for key, offset in self.other_offsets.items():
            if key != CAMERA_KEY:
                xoffset += offset[Xi]
                yoffset += offset[Yi]
        if not self.center[Xi]:
            xoffset += (self.width * effsize[Xi])/2
        if not self.center[Yi]:
            yoffset += (self.height * effsize[Yi])/2
        return [self.pos[Xi] + self.offset[Xi] + xoffset,
            self.pos[Yi] + self.offset[Yi] + yoffset]


    def getLeftSide(self):
        """returns the left side of the sprite, no matter where that might be"""
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
        for key, offset in list(self.other_offsets.items()):
            if key != CAMERA_KEY:
                xoffset += offset[Xi]
                yoffset += offset[Yi]
        return (self.pos[Xi] + xoffset - center_xoffset, self.pos[Yi] + yoffset - center_yoffset + height/2)


    def getRightSide(self, *args, **kwargs):
        return self.getRightSide(*args, **kwargs)

    def getRightSide(self):
        pos = self.getLeftSide()
        return (pos[0] + self.width * self.get_effective_size()[0], pos[1])

    def getBottomSide(self, *args, **kwargs):
        return self.getBottomSide(*args, **kwargs)

    def getBottomSide(self):
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
        for key, offset in list(self.other_offsets.items()):
            if key != CAMERA_KEY:
                xoffset += offset[Xi]
                yoffset += offset[Yi]
        return (self.pos[Xi] + xoffset - center_xoffset + width/2, self.pos[Yi] + yoffset - center_yoffset)

    def getTopSide(self, *args, **kwargs):
        return self.getTopSide(*args, **kwargs)

    def getTopSide(self):
        pos = self.getBottomSide()
        return (pos[0], pos[1] + self.height * self.get_effective_size()[1])

    def getBottomLeftCorner(self):
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
        for key, offset in list(self.other_offsets.items()):
            if key != CAMERA_KEY:
                xoffset += offset[Xi]
                yoffset += offset[Yi]
        return (self.pos[Xi] + xoffset - center_xoffset, self.pos[Yi] + yoffset - center_yoffset)

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

    def destroy(self):
        if Label_TTF is not None: #end of game error suppression:
            super(Label_TTF, self).destroy()
        self.setFollowCamera(False)
        self.remove_text()
