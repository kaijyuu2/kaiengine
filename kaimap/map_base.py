# -*- coding: utf-8 -*-

from .constants import *

from kaiengine.destroyinterface import DestroyInterface
from kaiengine.interface import ContainerElement
from kaiengine.resource import toStringPath
from kaiengine.jsonfuncs import jsonload

class TileProperties(DestroyInterface):
    def __init__(self, data = {}):
        self.tiledata = data
        
    def destroy(self):
        super().destroy()
        self.tiledata.clear()
        
class TileGraphic(SpriteElement):
    
    def setupTile(self, tiledata, xpos, ypos):
        newsprite = tiledata.get(MAP_TILE_GRAPHIC, None)
        if newsprite:
            self.setSprite(newsprite)
        self.setSpriteFlip(tiledata.get(MAP_TILE_XFLIP, False), tiledata.get(MAP_TILE_YFLIP, False))
        

class MapBase(ContainerElement):
    default_tile_properties_type = TileProperties
    default_tile_graphic_type = TileGraphic
    
    def __init__(self, map_path = None, tile_properties_type = None, tile_graphic_type = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if tile_properties_type is None:
            self.tile_properties_type = self.default_tile_properties_type
        else:
            self.tile_properties_type = tile_properties_type
        if tile_graphic_type is None:
            self.tile_graphic_type = self.default_tile_graphic_type
        else:
            self.tile_graphic_type = tile_graphic_type
        self.tile_properties = {}
        self.tile_layers = {}
        self.objects = {}
        self.map_height = 0
        self.map_width = 0
        self.map_tile_height = 1
        self.map_tile_width = 1
        
        if map_path is not None:
            self.loadMapFromPath(map_path)
            
    def setTilePropertiesType(self, tile_type):
        self.tile_properties_type = tile_type
        
    def setTileGraphicType(self, tile_type):
        self.tile_graphic_type = tile_type
        
    def clearMap(self):
        self.map_height = 0
        self.map_width = 0
        self.map_tile_height = 1
        self.map_tile_width = 1
        for tileprop in self.tile_properties.values():
            tileprop.destroy()
        self.tile_properties.clear()
        for obj in self.objects.values():
            obj.destroy()
        self.objects.clear()
        #TODO: the rest
            
    def loadMapFromPath(self, map_path):
        data = jsonload(toStringPath(map_path))
        self.clearMap()
        self.map_height = data.get(MAP_HEIGHT, 1)
        self.map_width = data.get(MAP_WIDTH, 1)
        self.map_tile_height = data.get(MAP_TILE_HEIGHT, 1)
        self.map_tile_width = data.get(MAP_TILE_WIDTH, 1)
        for i, tiledata in enumerate(data.get(MAP_TILE_PROPERTIES, [])):
            x = int(i % self.map_width)
            y = int(i / self.map_height)
            self.tile_properties[(x,y)] = self.tile_type(tiledata)
        for layernum, layer in enumerate(data.get(MAP_LAYERS, [])):
            if layer[MAP_LAYER_TYPE] == MAP_LAYER_TYPE_GRAPHIC:
                #graphic layer
                self.tile_layers[layernum] = {}
                for i, tiledata in enumerate(layer.get(MAP_TILE_GRAPHICS_LIST, [])):
                    x = int(i % self.map_width)
                    y = int(i / self.map_height)
                    self.tile_layers[layernum][(x,y)] = self.tile_graphic_type()
                    self.tile_layers[layernum][(x,y)].setupTile(tiledata, x, y)
                    self.tile_layers[layernum][(x,y)].setPos(x * self.map_tile_width, y * self.map_tile_height)
                    #TODO: hardcoding layers for now
                    self.tile_layers[layernum][(x,y)].setLayer(1000 + layernum)
            else:
                #object layer
                for objdata in layer.get(MAP_LAYER_OBJECTS_LIST, []):
                    self.parseObject(objdata, layernum)
                    
    
    def parseObject(self, objdata, layernum = 1):
        #simple object parser
        pass
        
        