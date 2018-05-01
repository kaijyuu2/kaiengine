# -*- coding: utf-8 -*-

from .scene import Scene

from kaiengine.sprite import SpriteMulti
from kaiengine.weakrefhelper import weakRef, unWeakRef
from kaiengine.objectinterface import GraphicalInterface

MAPTILE_SPRITE = "sprite"
MAPTILE_SPRITE_PRIORITY = "priority"
MAPTILE_SPRITE_XFLIP = "xflip"
MAPTILE_SPRITE_YFLIP = "yflip"

class TilemapScene(Scene):
    
    vars()[PATH] = copy.copy(TILEMAP_SCENE_FULL_PATH)
    default_prop = {TILEMAP_SCENE_TILE_LIST: [],
                TILEMAP_SCENE_WIDTH: 1,
                TILEMAP_SCENE_HEIGHT: 1,
                TILEMAP_SCENE_TILE_HEIGHT: 16,
                TILEMAP_SCENE_TILE_WIDTH: 16}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tilemap = {}
        
        self.loadTilemap()
        
    def secondaryInit(self):
        pass
    
    def getMapTileType(self):
        return MapTile
    
    def getMapTileWidth(self):
        return self.tile_width
    
    def getMapTileHeight(self):
        return self.tile_height
    
    
    def loadTilemap(self):
        self.clearMapTiles()
        xcounter = 0
        ycounter = self.height - 1
        for tile in self.tile_list:
            self.tilemap[(xcounter, ycounter)] = self.getMapTileType()(self)
            sprites = [None, None]
            priorities = [False, False]
            xflips = [False, False]
            yflips = [False, False]
            for key, index in SPRITE_DATA_SET:
                if key in tile:
                    sprites[index] = tile[key].get(MAPTILE_SPRITE, None)
                    priorities[index] = tile[key].get(MAPTILE_SPRITE_PRIORITY, False)
                    xflips[index] = tile[key].get(MAPTILE_SPRITE_XFLIP, False)
                    yflips[index] = tile[key].get(MAPTILE_SPRITE_YFLIP, False)
            self.tilemap[(xcounter, ycounter)].SetMaptileGraphics(sprites[0], sprites[1], priorities[0], priorities[1], xflips[0], xflips[1], yflips[0], yflips[1])
            self.tilemap[(xcounter, ycounter)].SetMaptilePos(xcounter, ycounter)
            xcounter += 1
            if xcounter >= self.width:
                xcounter = 0
                ycounter -= 1
                if ycounter < 0:
                    break #probable error
        
    def clearMapTiles(self):
        for tile in self.tilemap.values:
            tile.destroy()
        self.tilemap.clear()
        
    def destroy(self):
        super().destroy()
        self.clearMapTiles()
        
class MapTile(GraphicInterface):
    def __init__(self, mappe, *args, **kwargs):
        super().__init__(mappe, *args, **kwargs)
        self.owner = mappe
        
        self._priorities = [False, False]
        self._xflips = [False, False]
        self._yflips = [False, False]
        self.maptile_pos = [0,0]
        self.setSprite(SpriteMulti())
        self.setSpriteLayer(self.getNormalLayer())
        
    @property
    def owner(self):
        try:
            return unWeakRef(self._owner)
        except AttributeError:
            return None
    
    @owner.setter
    def owner(self, val):
        self._owner = weakRef(val)
        
    def getNormalLayer(self):
        return 1000
    
    def getPriorityLayer(self):
        return 10000

    def setMaptileGraphics(self, sprite1, sprite2, priority1, priority2, xflip1, xflip2, yflip1, yflip2):
        self._priorities = [priority1, priority2]
        self._xflips = [xflip1, xflip2]
        self._yflips = [yflip1, yflip2]
        if sprite1 != None:
            self._setMaptileMultiSprite(0, sprite1)
        else:
            self.sprite.remove_sprite(0)
        if sprite2 != None:
            self._setMaptileMultiSprite(1, sprite2)
        else:
            self.sprite.remove_sprite(1)

    def setMaptileSprite(self, layer, path):
        self.sprite.setMultiSprite(layer, self.getGraphicPath(path))
        self._setMaptileSprite(layer)

    def _setMaptileMultiSprite(self, layer, path):
        self.sprite.add_sprite(self.getGraphicPath(path), layer)
        self._setMaptileSprite(layer)

    def _setMaptileSprite(self, layer):
        self.sprite.setMultiLayer(layer, self.getPriorityLayer()  if self._priorities[layer] else self.getNormalLayer())
        self.sprite.setMultiFlip(layer, [self._xflips[layer], self._yflips[layer]])
        self.SetMaptilePos()

    def setMaptilePos(self, x = None, y = None):
        if x is None: x = self.maptile_pos[0]
        if y is None: y = self.maptile_pos[1]
        self.maptile_pos = [x,y]
        self.setPos(x * self.owner.getMapTileWidth(), y * self.owner.getMapTileHeight())

    def setMaptilePriority(self, layer, val):
        self._priorities[layer] = val
        self._setMaptileSprite(layer)

    def getMaptilePos(self):
        return self.maptile_pos[:]

    def getMaptileGraphicalPos(self):
        return self.getPos()

    def getMaptileGraphicalCenter(self):
        pos = self.GetMaptileGraphicalPos()
        return pos[0] + MAP_TILE_WIDTH/2, pos[1] + MAP_TILE_HEIGHT/2
        