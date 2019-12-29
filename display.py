

from kaiengine.gconfig import *
from kaiengine.debug import debugMessage
from .mainwindow import main_window
import os
from sys import platform

from . import sGraphics
from . import objects
from . import load
from . import camera
from .resource import toStringPath
from shutil import rmtree



# functions

def updateGraphics():
    camera.updateInternalCamera()
    camera.updateCameraSprites()
    sGraphics.graphicsUpdate()

def setupWindow(fullscreen=None, x = None, y = None, fake_fullscreen=None):
    from . import settings
    #initial setup of the main window
    if fake_fullscreen is None:
        try:
            fake_fullscreen = settings.getValue(DYNAMIC_SETTINGS_FAKE_FULLSCREEN)
        except:
            pass
    if fake_fullscreen:
        x, y = sGraphics.getScreenResolution()
        try:
            multiplier = x / settings.getValue(DYNAMIC_SETTINGS_WINDOW_DIMENSIONS)[0]
            ymultiplier = y / settings.getValue(DYNAMIC_SETTINGS_WINDOW_DIMENSIONS)[1]
            if multiplier != ymultiplier:
                debugMessage("WARNING: screen aspect ratio does not match for fake fullscreen! Setting to lower of possible values to avoid cutoff.")
                multiplier = min(multiplier, ymultiplier)
        except:
            debugMessage("WARNING: Error calculating multiplier for fake fullscreen (also check DYAMIC_SETTINGS_WINDOW_DIMENSIONS):\nWidth {0}\nHeight{1}".format(x, y))
            multiplier = 1
        setGlobalScaling(multiplier)
        settings.setValue(DYNAMIC_SETTINGS_GLOBAL_SCALING, multiplier)
        sGraphics.graphicsInitWindow(main_window(x, y, None, fake_fullscreen=True))

        #TODO: location to correct one for 2nd monitors, etc
        getWindow().set_location(0, 0)
    else:
        if x is None: x = int(settings.getValue(DYNAMIC_SETTINGS_WINDOW_DIMENSIONS)[0] * settings.getValue(DYNAMIC_SETTINGS_GLOBAL_SCALING))
        if y is None: y = int(settings.getValue(DYNAMIC_SETTINGS_WINDOW_DIMENSIONS)[1] * settings.getValue(DYNAMIC_SETTINGS_GLOBAL_SCALING))
        if fullscreen is None: fullscreen = settings.getValue(DYNAMIC_SETTINGS_FULLSCREEN)
        sGraphics.graphicsInitWindow(main_window(x, y, fullscreen))

def getWindow():
    return sGraphics.getGameWindow()

def getWindowDimensions():
    return getWindow().get_size()

def getWindowDimensionsScaled():
    dim = getWindowDimensions()
    scaling = sGraphics.getGlobalScaling()
    return dim[0] / scaling, dim[1] / scaling

def getGlobalScaling():
    return sGraphics.getGlobalScaling()

def setGlobalScaling(scaling):
    sGraphics.setGlobalScaling(scaling)

def setWindowDimensions(x = None, y = None, skipCheck=False, forceSize=False):
    dimensions = getWindowDimensions()
    getWindow().set_dimensions(x or dimensions[0], y or dimensions[1], skipCheck=skipCheck, forceSize=forceSize)

def setWindowDimensionsScaled(x = None, y = None, *args, **kwargs):
    dimensions = getWindowDimensionsScaled()
    x = x or dimensions[0]
    y = y or dimensions[1]
    scaling = getGlobalScaling()
    setWindowDimensions(x * scaling, y * scaling, *args, **kwargs)

def setWindowLogo(*logos):
    getWindow().set_icon(*logos)

def hideWindowCursor():
    """Wrapper for whatever we need to do to hide the hardware cursor."""
    getWindow().set_mouse_visible(False)

def toggleWindowFullscreen(value=None, stretch=False, dimensions=None):
    """Toggle fullscreen mode on/off."""
    #NOTE: STILL BUGGY
    if value == getWindow().fullscreen: return
    if value is None:
        value = not getWindow().fullscreen
    if value and stretch:
        screen = getWindow().display.get_default_screen()
        maxWidthMultiplier = screen.width / (1.0*getWindowDimensionsScaled()[0])
        maxHeightMultiplier = screen.height / (1.0*getWindowDimensionsScaled()[1])
        newScale = min(maxWidthMultiplier, maxHeightMultiplier)
        newSize = (int(getWindowDimensionsScaled()[0]*newScale), int(getWindowDimensionsScaled()[1]*newScale))
        setGlobalScaling(newScale)
        getWindow().set_fullscreen(value, width=newSize[0], height=newSize[1])
    else:
        if dimensions is None:
            screen = getWindow().display.get_default_screen()
            newScale = int(min(screen.width/640, screen.height/400))
            newSize = (int(getWindowDimensionsScaled()[0]*newScale), int(getWindowDimensionsScaled()[1]*newScale))
            setGlobalScaling(newScale)
            getWindow().set_fullscreen(value, width=newSize[0], height=newSize[1])
        else:
            getWindow().set_fullscreen(value, width=dimensions[0], height=dimensions[1])



#graphic creation functions. Use these if you want to use a sprite or label

def createGraphic(path, layer = -1, *args, **kwargs):
    #generic loader for all graphic types
    if path is None:
        return createSprite(path, layer, *args, **kwargs)
    path = toStringPath(path)
    ext = os.path.splitext(path)[1]
    if ext == PNG_EXTENSION:
        return createSprite(path, layer, *args, **kwargs)
    if ext == GRAPHIC_OBJECT_EXTENSION:
        return createGraphicObject(path, layer, *args, **kwargs)
    if ext == LABEL_OBJECT_EXTENSION:
        return createLabelObject(path, layer, *args, **kwargs)
    if ext == BORDERED_SPRITE_EXTENSION:
        return createBorderedSprite(path, layer, *args, **kwargs)
    if ext == MULTI_SPRITE_EXTENSION:
        return createMultiSprite(path, layer, *args, **kwargs)
    debugMessage("graphic of unsupported format: " + path)
    if len(ext) == 0:
        debugMessage("You forgot to include the extension, methinks")
    return None

def createLabel(text, font_size = DEFAULT_TEXT_SIZE, font = DEFAULT_FONT, color = DEFAULT_TEXT_COLOR, layer = -1, *args, **kwargs):
    #for making any sort of text without using an external label file
    from .label import Label
    return Label(layer = layer, text = text, font_size = font_size, font = font, color = color, *args, **kwargs)

#specialty sprites

def createSpritePlaceholder(path, *args, **kwargs):
    #for preemptively putting some sprite graphics in vram so they don't have to be loaded during gameplay.
    from .sprite import SpritePlaceholder
    return SpritePlaceholder(path, *args, **kwargs)

def createGlowSprite(path, *args, **kwargs):
    from .sprite import SpriteGlow
    return SpriteGlow(path, *args, **kwargs)

def createBorderedSprite(path, *args, **kwargs):
    from .sprite import SpriteBordered
    data = load.loadGenericObj(path, BORDERED_SPRITE_EXTENSION)
    try: data.pop(CLASS_TYPE) #unused; remove if it's there
    except KeyError: pass
    return SpriteBordered(data, *args, **kwargs)

def createMultiSprite(path, *args, **kwargs):
    from .sprite import SpriteMulti
    data = load.loadGenericObj(path, MULTI_SPRITE_EXTENSION)
    try: data.pop(CLASS_TYPE) #unused; remove if it's there
    except KeyError: pass
    return SpriteMulti(data, *args, **kwargs)

def createBarebonesSprite(path, *args, **kwargs):
    from .sGraphics import sSprite
    return sSprite(path, *args, **kwargs)


#internal use only. Do not use.
def createSprite(path, layer = -1, *args, **kwargs):
    from .sprite import Sprite
    return Sprite(path, layer, *args, **kwargs)

def createLabelObject(path, layer = -1, *args, **kwargs):
    prop = load.load_label_object(path)
    #defaults
    font_size = DEFAULT_TEXT_SIZE
    font = DEFAULT_FONT
    color = DEFAULT_TEXT_COLOR
    text = ""
    if LABEL_OBJECT_TEXT in prop:
        text = prop[LABEL_OBJECT_TEXT]
        prop.pop(LABEL_OBJECT_TEXT)
    if LABEL_OBJECT_TEXT_SIZE in prop:
        font_size = prop[LABEL_OBJECT_TEXT_SIZE]
        prop.pop(LABEL_OBJECT_TEXT_SIZE)
    if LABEL_OBJECT_FONT in prop:
        font = prop[LABEL_OBJECT_FONT]
        prop.pop(LABEL_OBJECT_FONT)
    if LABEL_OBJECT_COLOR in prop:
        color = prop[LABEL_OBJECT_COLOR]
        prop.pop(LABEL_OBJECT_COLOR)
    prop.update(kwargs)
    return createLabel(text, font_size, font, color, layer, *args, **prop)

def createGraphicObject(path, layer, *args, **kwargs):
    data = load.loadGenericObj(path, GRAPHIC_OBJECT_EXTENSION)
    gfxtype = data[CLASS_TYPE]
    data.pop(CLASS_TYPE)
    return createGraphicObjectDirect(gfxtype, data, layer, *args, **kwargs)

def createGraphicObjectDirect(gfxtype = None, path = None, layer = -1, *args, **kwargs):
    return objects.createGraphicObject(gfxtype, path, layer = layer, *args, **kwargs)
