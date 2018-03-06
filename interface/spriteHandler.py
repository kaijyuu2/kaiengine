'''Abstracts away the creation, destruction, and updating of sprites.'''

from kaiengine.gconfig import *
from kaiengine import sDict
from kaiengine.objectdestroyederror import ObjectDestroyedError
from kaiengine.resource import checkResourceExists, toStringPath
from kaiengine.display import createSpritePlaceholder, createGraphic
from kaiengine.debug import debugMessage

sprites = sDict.sDict()
preloadedSprites = {}

def preloadSprite(path):
    '''Preloads a sprite, ensuring its resource is kept available.'''
    path = _verifyPath(path)
    if path in preloadedSprites:
        return
    preloadedSprites[path] = createSpritePlaceholder(path)

def checkSpriteExists(spritePath):
    return checkResourceExists(_verifyPath(spritePath))

def registerSprite(sprite):
    '''Add an already-made sprite (perhaps from a label or something) to the automatic update list, if it isn't already on the list.'''
    if hasattr(sprite, "ID"):
        return sprite
    ID = sprites.append(sprite)
    sprites.last_item().ID = ID
    return sprites.last_item()

def makeSprite(path, layer=-1):
    '''Create and return a sprite (which is also added to the update list).'''
    return registerSprite(createGraphic(_verifyPath(path), layer = layer))

def makeUISprite(path, layer=-1):
    '''Convenience function for making sprites that follow the camera.'''
    #DEPRECATED
    sprite = makeSprite(path, layer)
    #sprite.follow_camera = True
    return sprite

def removeSprite(sprite):
    '''Destroy a sprite.'''
    ID = sprite.ID
    try:
        sprites[ID].destroy()
        del sprites[ID]
    except KeyError:
        pass

def getSpriteByID(ID):
    '''Get a sprite by its internal ID.'''
    return sprites[ID]

def processSprites():
    '''Call once per graphical frame to update all on-screen sprites'''
    for sprite in list(sprites.values()):
        try:
            sprite.run()
        except ObjectDestroyedError:
            debugMessage("WARNING: Destroyed sprite still in memory! Deleting.")
            ID = sprite.ID
            del sprites[ID]

def updateSpriteImage(sprite, imagePath):
    '''Changes a sprite's image if it differs from path.'''
    imagePath = _verifyPath(imagePath)
    #TODO ALPHA2?: make sure this works OK with archived resources...
    sprite.set_image(imagePath)

def destroyAllSprites():
    '''Destroys all sprites.'''
    global sprites
    for sprite in list(sprites.values()):
        try:
            sprite.destroy()
        except ObjectDestroyedError:
            pass
    sprites = sDict.sDict()

def clearPreloadedSprites():
    '''Purge all preloaded sprites, potentially unloading their data.'''
    global preloadedSprites
    for sprite in list(preloadedSprites.values()):
        try:
            sprite.destroy()
        except ObjectDestroyedError:
            pass
    preloadedSprites = {}



def _verifyPath(path):
    '''adds resource and graphics to the path if needed'''
    if RESOURCE_PATH in path and GRAPHICS_PATH in path:
        return toStringPath(*path)
    else:
        return toStringPath(RESOURCE_PATH, GRAPHICS_PATH, *path)
