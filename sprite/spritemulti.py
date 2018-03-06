
from kaiengine.gconfig import *
import kaiengine.display as display
import kaiengine.graphicobject as graphicobject
from kaiengine.resource import toStringPath
import os
import traceback

class SpriteMulti(graphicobject.GraphicObject):

    vars()[EXTENSION] = MULTI_SPRITE_EXTENSION

    default_prop = {MULTI_SPRITE_SPRITES: {}}

    def __init__(self,path = {}, *args, **kwargs):
        super(SpriteMulti, self).__init__(path, *args, **kwargs)
        self._spriteLayers = {}
        self._sprite_flips = {}
        try: self._gfx_path = path[FILEPATH][:]
        except KeyError: self._gfx_path = []

        self._loadSprites()


    @property
    def width(self):
        if len(self.sprites) > 0:
            return self.sprites.last_item().width
        else:
            return 0
    @width.setter
    def width(self, newvalue):
        for sprite in list(self.sprites.values()):
            sprite.width = newvalue

    @property
    def height(self):
        if len(self.sprites) > 0:
            return self.sprites.last_item().height
        else:
            return 0
    @height.setter
    def height(self, newvalue):
        for sprite in list(self.sprites.values()):
            sprite.height = newvalue

    @property
    def center(self):
        if len(self.sprites) > 0:
            return self.sprites.last_item().center
        else:
            return (False,False)
    @center.setter
    def center(self, *args, **kwargs):
        for sprite in list(self.sprites.values()):
            sprite.setCenter(*args, **kwargs)

    def update_layer(self):
        for key, sprite in list(self.sprites.items()):
            try: layer_offset = self._spriteLayers[key]
            except KeyError: layer_offset = 0
            sprite.layer = self.layer + layer_offset

    def update_flip(self):
        for key, sprite in list(self.sprites.items()):
            try: flips = self._sprite_flips[key]
            except KeyError: flips = [False, False]
            sprite.setFlip(*flips)


    def setOffset(self, *args, **kwargs):
        for sprite in list(self.sprites.values()):
            sprite.setOffset(*args, **kwargs)

    def set_dimensions(self, *args, **kwargs):
        for sprite in list(self.sprites.values()):
            sprite.set_dimensions(*args, **kwargs)

    def setPos(self, *args, **kwargs):
        super(SpriteMulti, self).setPos(*args, **kwargs)
        for sprite in list(self.sprites.values()):
            sprite.setPos(*self.pos)

    def remove_sprite(self, key = None):
        if key == None:
            try: key = sorted(self.sprites.keys())[0]
            except IndexError: key = None
        super(SpriteMulti, self).remove_sprite(key)
        try: del self._spriteLayers[key]
        except KeyError: pass

    def remove_sprites(self):
        super(SpriteMulti, self).remove_sprites()
        self._spriteLayers.clear()

    def setMultiLayer(self, key, layer):
        self._spriteLayers[key] = layer
        self.update_layer()

    def setMultiFlip(self, key, flip):
        self._sprite_flips[key] = flip
        self.update_flip()

    def setMultiSprite(self, key, path):
        self.remove_sprite(key)
        self.add_sprite(path, key)

    def _loadSprites(self):
        for sprite in self.multi_sprites:
            try:
                key = self.add_sprite(toStringPath(self._gfx_path + [sprite[MULTI_SPRITE_SPRITE_PATH]]))
                try: self._spriteLayers[key] = sprite[MULTI_SPRITE_SPRITE_LAYER]
                except KeyError: pass
            except KeyError:
                pass
        self.update_layer()
