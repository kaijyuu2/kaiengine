

from kaiengine.gconfig import *
import copy
from kaiengine.resource import checkResourceExists, toStringPath

FontDriverObj = None

def initializeFontDriver():
    from . import fontdriver
    global FontDriverObj
    FontDriverObj = fontdriver.FontDriver()

def initializeFonts():
    from kaiengine import load
    fontslist = load.load_font_paths()
    for newfont in fontslist:
        FontDriverObj.add_font(newfont)

def closeFonts(): #for end of game
    if FontDriverObj is not None:
        FontDriverObj.destroy()

def getFontPath(*args):
    #extension not added
    if len(args) > 0:
        filepath = toStringPath(*args)
        if RESOURCE_PATH not in filepath:
            path2 = copy.copy(FULL_FONT_PATH)
            path2.append(filepath)
            filepath = toStringPath(*path2)
    else:
        filepath = toStringPath(*FULL_FONT_PATH)
    return filepath

def checkGlyphExists(glyph_path):
    glyph_path = getFontPath(glyph_path)
    return checkResourceExists(glyph_path)

def getWidth(text, font_size, font_path):
    font_path = getFontPath(font_path)
    return FontDriverObj.get_width(text, font_size, font_path)

def getHeight(font_size, font_path):
    font_path = getFontPath(font_path)
    return FontDriverObj.get_height(font_size, font_path)

def getDim(text, font_size, font_path, font = None):
    font_path = getFontPath(font_path)
    return FontDriverObj.get_dim(text, font_size, font_path)

def textToImage(text, font_size = DEFAULT_TEXT_SIZE, font_path = DEFAULT_FONT):
    font_path = getFontPath(font_path)
    return FontDriverObj.text_to_image(text, font_size, font_path)

def textToImageBuffer(text, font_size = DEFAULT_TEXT_SIZE, font_path = DEFAULT_FONT, bordered = False, borderInverse = False, borderColor = COLOR_BLACK):
    font_path = getFontPath(font_path)
    return FontDriverObj.text_to_image_buffer(text, font_size, font_path, bordered=bordered, borderInverse=borderInverse, borderColor=borderColor)

def getSpriteList(text, font_path, font_size = MENU_TEXT_SIZE):
    font_path = getFontPath(font_path)
    return FontDriverObj.get_sprite_list(text, font_path, font_size)

def getDefaultFontSize(font_path):
    font_path = getFontPath(font_path)
    return FontDriverObj.get_default_font_size(font_path)
