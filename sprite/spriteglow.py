

#sprite glow effects
#slow, use sparingly

from .sprite import Sprite

from kaiengine.resource import ResourceUnavailableError
from kaiengine.sGraphics import loadImageData
from kaiengine.display import createGlowSprite
from kaiengine.debug import debugMessage

from PIL import Image
from numpy import array, nextafter


GLOW_ID = "_GLOW_ID"

class SpriteGlow(Sprite):

    def __init__(self, *args, **kwargs):
        super(SpriteGlow,self).__init__(*args, **kwargs)
        self._glow_sprite = None

    def setPos(self, *args, **kwargs):
        super(SpriteGlow, self).setPos(*args, **kwargs)
        self._updateGlowPos()

    def setLayer(self, *args, **kwargs):
        super(SpriteGlow, self).setLayer(*args, **kwargs)
        self._updateGlowLayer()

    def setOffset(self, *args, **kwargs):
        super(SpriteGlow, self).setOffset(*args, **kwargs)
        self._updateGlowOffset()

    def setWidth(self, *args, **kwargs):
        super(SpriteGlow, self).setWidth(*args, **kwargs)
        self._updateGlowDimensions()

    def setHeight(self, *args, **kwargs):
        super(SpriteGlow, self).setHeight(*args, **kwargs)
        self._updateGlowDimensions()

    def setTexWidths(self, *args, **kwargs):
        super(SpriteGlow, self).setTexWidths(*args, **kwargs)
        self._updateGlowTexDimensions()

    def setTexHeights(self, *args, **kwargs):
        super(SpriteGlow, self).setTexHeights(*args, **kwargs)
        self._updateGlowTexDimensions()

    def setShow(self, *args, **kwargs):
        super(SpriteGlow, self).setShow(*args, **kwargs)
        self._updateGlowShow()

    def setCenter(self, *args, **kwargs):
        super(SpriteGlow, self).setCenter(*args, **kwargs)
        self._updateGlowCenter()

    def setFlip(self, *args, **kwargs):
        super(SpriteGlow, self).setFlip(*args, **kwargs)
        self._updateGlowFlip()

    def setSize(self, *args, **kwargs):
        super(SpriteGlow, self).setSize(*args, **kwargs)
        self._updateGlowSize()

    def append_offset(self, *args, **kwargs):
        super(SpriteGlow, self).append_offset(*args, **kwargs)
        self._updateGlowOtherOffsets()

    def remove_offset(self, *args, **kwargs):
        super(SpriteGlow, self).remove_offset(*args, **kwargs)
        self._updateGlowOtherOffsets()

    def change_offset(self, *args, **kwargs):
        super(SpriteGlow, self).change_offset(*args, **kwargs)
        self._updateGlowOtherOffsets()


    def _updateGlowPos(self):
        try:
            self._glow_sprite.setPos(*self.pos)
        except AttributeError:
            pass

    def _updateGlowLayer(self):
        if self._glow_sprite is not None: #if faster than try/catch here due to the nextafter call being very expensive
            self._glow_sprite.layer = nextafter(self.layer, self.layer +1) #get the smallest increment possible for a float

    def _updateGlowOffset(self):
        try:
            self._glow_sprite.setOffset(*self.offset)
        except AttributeError:
            pass

    def _updateGlowDimensions(self):
        try:
            self._glow_sprite.set_dimensions(self.width, self.height)
        except AttributeError:
            pass

    def _updateGlowTexDimensions(self):
        try:
            self._glow_sprite.set_texture_dimensions(self.tex_widths[0], self.tex_widths[1],self.tex_heights[0], self.tex_heights[1])
        except AttributeError:
            pass

    def _updateGlowShow(self):
        try:
            self._glow_sprite.show = self.show
        except AttributeError:
            pass

    def _updateGlowCenter(self):
        try:
            self._glow_sprite.setCenter(*self.center)
        except AttributeError:
            pass

    def _updateGlowFlip(self):
        try:
            self._glow_sprite.setFlip(*self.flip)
        except AttributeError:
            pass

    def _updateGlowSize(self):
        try:
            for key, val in list(self._size.items()):
                self._glow_sprite.setSize(val[0],val[1],key)
        except AttributeError:
            pass

    def _updateGlowOtherOffsets(self):
        try:
            for key, val in list(self.other_offsets.items()):
                self._glow_sprite.change_offset(key, *val)
        except AttributeError:
            pass


    def setGlow(self, r = None, g = None, b = None, a = None):
        if not self.destroyed:
            self.enableGlow()
            colors = self._glow_sprite.color
            if r is None:
                r = colors[0]
            if g is None:
                g = colors[1]
            if b is None:
                b = colors[2]
            if a is None:
                a = self._glow_sprite.alpha
            if self._glow_sprite.color != [r,g,b]:
                self._glow_sprite.color = [r,g,b]
            if self._glow_sprite.alpha != a:
                self._glow_sprite.alpha = a

    def enableGlow(self):
        if self._glow_sprite is None and self.image_path is not None:
            self._glow_sprite = createGlowSprite(None)
            self._glow_sprite._setGlowImage(self.image_path)
            self.updateGlowSprite()

    def disableGlow(self):
        if self._glow_sprite is not None:
            self._glow_sprite.destroy()
            self._glow_sprite = None

    def updateGlowSprite(self):
        #forcibly update everything
        self._updateGlowPos()
        self._updateGlowCenter()
        self._updateGlowOffset()
        self._updateGlowOtherOffsets()
        self._updateGlowSize()
        self._updateGlowFlip()
        self._updateGlowTexDimensions()
        self._updateGlowDimensions()
        self._updateGlowShow()
        self._updateGlowLayer()


    def _setGlowImage(self, image_path):
        try:
            self.set_image_from_buffer(self._GetGlowTexID(image_path), *self._CreateTexture(image_path))
        except ResourceUnavailableError:
            debugMessage("Failure to create glow image. Might be due to current incompatibility with dynamic textures (ttf text, etc).")


    def _CreateTexture(self, image_path):
        try:
            xdim, ydim, baseimage = loadImageData(image_path)
        except ResourceUnavailableError:
            raise ResourceUnavailableError("Glow only compatible with non-dynamic textures! IE, loaded images.")
        r, g, b, a = baseimage.split() #nab the alpha values
        newimage = Image.new('RGBA',(xdim, ydim), (255,255,255,0)) #create image of appropriate size
        mask = Image.merge("L",(a,)) #turn alpha list into an image for masking
        newimage.putalpha(mask) #create the alpha layer of new image
        image_data = array(newimage.convert("RGBA"), 'B') #convert to stuff numpy and opengl understands
        return xdim, ydim, image_data

    def _GetGlowTexID(self, image_path):
        return image_path + GLOW_ID

    def destroy(self):
        super().destroy()
        self.disableGlow()
