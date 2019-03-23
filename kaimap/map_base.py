# -*- coding: utf-8 -*-

from kaiengine.interface import ContainerElement
from kaiengine.resource import toStringPath
from kaiengine.jsonfuncs import jsonload

class MapBase(ContainerElement):
    default_tile_type = None
    
    def __init__(self, map_path = None, tile_type = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if tile_type is None:
            self.tile_type = self.default_tile_type
        else:
            self.tile_type = tile_type
        self.tile_properties = {}
        self.tile_layers = []
        self.map_height = 0
        self.map_width = 0
        
        if map_path is not None:
            self.loadMapFromPath(map_path)
            
    def setTileType(self, tile_type):
        self.tile_type = tile_type
            
    def loadMapFromPath(self, map_path):
        data = jsonload(toStringPath(map_path))
        self.map_height = data.get(MAP_HEIGHT)