

from .interfaceLayer import InterfaceLayer

baselayer = None



def initializeBaseLayer(layer_type = None, *args, **kwargs):
    global baselayer
    if layer_type is None: #default is incredibly basic layer
        layer_type = InterfaceLayer
    baselayer = layer_type(None, None, *args, **kwargs)

def getBaseLayer():
    return baselayer

def addLayer(*args, **kwargs):
    return getBaseLayer().addTopLayer(*args, **kwargs)

def destroyLayers():
    global baselayer
    if baselayer is not None:
        baselayer.deleteHigherLayers()
        baselayer.destroy()
        baselayer = None
