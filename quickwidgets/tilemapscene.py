# -*- coding: utf-8 -*-

from .toplevelelements import Scene

from kaiengine.interface import ScreenElement
from kaiengine.kaiobject import KaiObject, createObjectWithData
from kaiengine.weakrefhelper import weakRef, unWeakRef
from kaiengine.uidgen import IdentifiedObject
from kaiengine.destroyinterface import DestroyInterface
from kaiengine.debug import debugMessage
from kaiengine.gameframehandler import resetLag
from kaiengine.gconfig import RESOURCE_PATH, GRAPHICS_PATH, FULL_GRAPHIC_PATH

from collections import defaultdict
import copy

#tilemap scenes

TILEMAP_SCENE_EXTENSION = ".map"
DEFAULT_TILEMAP_SCENE_DIR = "maps"
DEFAULT_TILEMAP_SCENE_PATH = (RESOURCE_PATH, DEFAULT_TILEMAP_SCENE_DIR)

TILEMAP_SCENE_TILE_DATA_LIST = "tile_data_list"
TILEMAP_SCENE_TILE_GRAPHIC_DICT = "tile_graphic_dict"
TILEMAP_SCENE_MAP_OBJECT_DICT = "map_object_dict"
TILEMAP_SCENE_WIDTH = "map_width"
TILEMAP_SCENE_HEIGHT = "map_height"
TILEMAP_SCENE_TILE_HEIGHT = "tile_height"
TILEMAP_SCENE_TILE_WIDTH = "tile_width"

MAPTILE_POS = "pos"
MAPTILE_SPRITE_DATA = "graphic_data"
MAPTILE_SPRITE = "graphic"
MAPTILE_SPRITE_XFLIP = "xflip"
MAPTILE_SPRITE_YFLIP = "yflip"

DEFAULT_MAPTILE_GRAPHIC_PATH = (RESOURCE_PATH, GRAPHICS_PATH)


class MapTileData(IdentifiedObject, DestroyInterface):
    
    def __init__(self, *args, maptile_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.maptile_position = maptile_data[MAPTILE_POS]
        
class MapTileGraphic(ScreenElement):
    graphic_path = copy.copy(DEFAULT_MAPTILE_GRAPHIC_PATH)
    
    def __init__(self, *args, maptile_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.maptile_position = maptile_data[MAPTILE_POS]
        
        if MAPTILE_SPRITE in maptile_data:
            self.setSprite(maptile_data[MAPTILE_SPRITE])
            self.setSpriteFlip(maptile_data.get(MAPTILE_SPRITE_XFLIP, False), maptile_data.get(MAPTILE_SPRITE_YFLIP, False))
    

class TilemapScene(Scene, KaiObject):
    
    default_prop = {TILEMAP_SCENE_TILE_DATA_LIST: [],
                    TILEMAP_SCENE_TILE_GRAPHIC_DICT: {},
                    TILEMAP_SCENE_MAP_OBJECT_DICT: {},
                    TILEMAP_SCENE_WIDTH: 1,
                    TILEMAP_SCENE_HEIGHT: 1,
                    TILEMAP_SCENE_TILE_HEIGHT: 16,
                    TILEMAP_SCENE_TILE_WIDTH: 16}
    
    map_tile_data_type = MapTileData
    map_tile_graphic_type = MapTileGraphic
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tile_graphics_map = defaultdict(dict) #contains screen element ids
        self.objects_map = defaultdict(list) #contains screen element ids
        self.tile_data_map = {} #does not contain screen element ids, contains tile data objects. tile data objects are not screen elements
        
        self.loadTilemap()
        self.loadObjects()
        
        
    
    def getMapTileDataType(self, tiledata = None):
        return self.map_tile_data_type
    
    def setMapTileDataType(self, newtype):
        self.map_tile_data_type = newtype
        
    def getMapTileGraphicType(self, tiledata = None):
        return self.map_tile_graphic_type
    
    def setMapTileGraphicType(self, newtype):
        self.map_tile_graphic_type = newtype
    
    def getMapTileWidth(self):
        return self.tile_width
    
    def getMapTileHeight(self):
        return self.tile_height
    
    
    def loadTilemap(self):
        self.clearMapTiles()
        for tile in self.tile_data_list:
            try:
                pos = tuple(tile[MAPTILE_POS])
                self.tile_data_map[pos] = self.createMapTileData(maptile_data = tile)
            except KeyError:
                debugMessage("Map tile data lacked position.")
                debugMessage(str(tile))
        for layer, tilelist in self.tile_graphic_dict.items():
            layer = int(layer) #since probably a string
            for tile in tilelist:
                try:
                    pos = tuple(tile[MAPTILE_POS])
                    tilechild = self.addChild(self.createMapTileGraphic(maptile_data = tile), False)
                    self.tile_graphics_map[layer][pos] = tilechild.id
                    tilechild.setElementPosition(pos[0] * self.tile_width, pos[1] * self.tile_height)
                except KeyError:
                    debugMessage("Map tile graphic lacked position.")
                    debugMessage(str(tile))
                
                    
    def loadObjects(self):
        self.clearMapObjects()
        #TODO: implement
        
    def updateChildrenLayers(self, lastlayer = None):
        #should return the highest used layer
        if not lastlayer:
            lastlayer = self.getLayer()
        baselayer = lastlayer + 1 #first layer is bg
        for layer, data in self.tile_graphics_map.items():
            newlayer = baselayer + layer
            for element_id in data.values():
                self.getChild(element_id).setLayer(newlayer)
            lastlayer = max(lastlayer, newlayer)
        for layer, data in self.objects_map.items():
            newlayer = baselayer + layer
            for element_id in data:
                self.getChild(element_id).setLayer(newlayer)
            lastlayer = max(lastlayer, newlayer)
        lastlayer = super().updateChildrenLayers(lastlayer) #include scene's code
        return lastlayer
        
        
    def clearMapTiles(self):
        for tile in self.tile_data_map.values():
            tile.destroy()
        for layerdata in self.tile_graphics_map.values():
            for tileid in layerdata.values():
                try:
                    self.removeChild(tileid)
                except KeyError:
                    pass
        self.tile_data_map.clear()
        self.tile_graphics_map.clear()
        
    def clearMapObjects(self):
        for layerdata in self.objects_map.values():
            for obj in layerdata:
                obj.destroy()
        self.objects_map.clear()
        
    def createMapTileData(self, *args, maptile_data, **kwargs):
        return self.getMapTileDataType(maptile_data)(*args, maptile_data = maptile_data, *kwargs)
    
    def createMapTileGraphic(self, *args, maptile_data, **kwargs):
        return self.getMapTileGraphicType(maptile_data)(*args, maptile_data = maptile_data, **kwargs)
        
    def destroy(self):
        super().destroy()
        self.clearMapTiles()
        self.clearMapObjects()
        self.map_tile_type = None
        
def createTilemapScene(filename, *args, **kwargs):
    return createObjectWithData(filename, DEFAULT_TILEMAP_SCENE_PATH, TILEMAP_SCENE_EXTENSION, TilemapScene, *args, **kwargs)