

from .cannotresizewindowerror import CannotResizeWindowError
from .invalidscreenshotcoordinateserror import InvalidScreenshotCoordinatesError

#currently force opengl
from .sGraphicsOpenGL import *

"""

sGraphics documentation!

All functions/classes should act identically as far as the user is concerned regardless of what graphics libraries (opengl, etc) are being used



Functions:

GraphicsInit(window_x, window_y)
Initialization that should be called at the beginning of the game.
Remember to pass the window x/y dimensions

GraphicsInitWindow(window)
Same as graphics init, but if you want to use a derivative of the sWindow class, pass an initialized version to this

GetGameWindow()
returns a reference to the GameWindow

GraphicsUpdate()
Should be run at the end of every frame (not draw frame, but game frame)
This updates VRAM so things that have been changed this frame will display correctly.

FixColorValues(colors):
Pass a list of colors in either float format (0.0-1.0) or integer format (0-255) and it returns the correctly formatted colors
Possible issue: using a value of 1.0 will be interpreted as as 100% color, which may have been intended to be near-black.
Color list format: [red, green, blue]
If an alpha is passed at the end of the list, the returned tuple will include it untouched.

FixColorValuesFloats(colors):
Forces fixColorValues to return a tuple of floats.

FixColorValuesIntegers(colors):
Forces fixColorValues to return a tuple of integers.

GetTextureDimensions(path)
Returns the dimensions of the texture at path
Can be used for textures created through buffers (by passing the name), but will throw an error if it doesn't exist

SetGlobalScaling(value)
Sets the global scaling of everything. 1 is default.

getGlobalScaling()
Returns what the global scaling is set to. Returns -1 on error

setCameraXY(x, y):
Sets the xy position of the internal camera

getCameraXY():
returns the xy position of t he internal camera


Classes:

sSprite

    (functions)

    __init__(self, image_path = None, antialiasing = None)
    Initialization. Pass an image path to give it an image to draw upon creation.
    If your image is a buffer, pass that to add_image_from_buffer after creation

    setPos(self, x = None, y = None)
    Sets the x/y position. Superior to just setting the pos attribute since you can set either x or y individually.

    setOffset(self, x = None, y = None)
    Sets the x/y draw offset.

    append_offset(self, x = 0, y = 0)
    Pass an offset list to further offset a sprite (for a camera system/etc)
    Both x and y must be specified here
    returns an index to the other_offsets attribute

    remove_offset(self, index)
    Removes an offset list from the other_offsets list
    Throws no error if index isn't found

    change_offset(self, index, x = None, y = None)
    Changes an offset in the other_offsets list.
    Sets the update_image flag, unlike setting the other_offsets attribute directly would
    If index does not exist, a new one is created.

    set_dimensions(self, width = None, height = None)
    Sets the width and height of the sprite, if you want it different from the image file's sizes

    set_texture_dimensions(self, xLeft = None, xRight = None, yBottom = None, yTop = None)
    Sets the texture dimensions, for things like tiling the texture.
    Uses floats and goes from 0.0 to 1.0 (1.0 spans the length of the image)
    Basic state is: xLeft = 0.0, xRight = 1.0, yBottom = 0.0, yTop = 1.0

    tileTexture(self, xfactor = 1.0, yfactor = 1.0)
    Convenience function for set_texture_dimensions
    Automatically sets the texture dimensions while taking into account the sprite's dimensions,
    such that the texture will appear tiled appropriately.
    Set to 1.0 means that the texture will appear tiled at its original size.
    Setting to 2.0 means it will appear twice as large, and 0.5 half, etc.

    crop(self, left, bottom, right, top)
    Crop sprite to specified edges.
    Doesn't currently work with animated sprites (I think...?)
    Will probably give weird results for values larger than initial dimensions.

    setSize(self, x = None, y = None, key = DEFAULT_SIZE_KEY)
    Sets the sprite's size multiplier
    Is a float. 1.0 would change nothing, 2.0 would double the size, and 0.5 would halve it
    Specifying a key will allow you to create a new size modifier on top of the default one.
    They stack multiplicatively (two 3.0 size mods will result in an effective size of 9.0)

    get_size(self, key = DEFAULT_SIZE_KEY)
    Returns the sprite's size multiplier
    See setSize for details on what size does
    Returns [1.0,1.0] with an invalid key

    remove_size(self, key):
    Removes the selected size key.
    Does nothing if key doesn't exist

    resetSize(self)
    Removes all size modifiers, resetting the sprite's size to 1 in both directions

    setColor(self, r = None, g = None, b = None, alpha = None)
    Sets the coloring of the sprite.
    Please use floats for color (0.0 - 1.0) and not integers.
    The alpha value is completely ignored.

    setCenter(self, x = None, y = None)
    Sets the centering of the sprite. Uses booleans.
    This will essentially move the origin point by half the sprite's length

    setFlip(self, x = None, y = None)
    Sets the flip of the sprite. Uses booleans.
    Will not affect positioning; will just flip the texture.

    (note: See properties list below for other attributes that can be changed)

    set_image(self, image_path, tex_id = None, keep_dim = False, display = True, antialiasing = None)
    Adds an image from path. This should be a regular string, properly formatted for the OS.
    If you know this image has already been given a texture id, you may pass it (though this isn't required)
    In fact, try not to pass a tex_id. It's mostly for internal use
    keep_dim being set to true means that the width, height and texture dimension attributes will be unchanged from the previous image
    If display is set to false, the game won't attemt to draw the image.
    This is NOT the same as unsetting the show flag, since you won't be able to undo it.
    Setting display to false is for pre-loading textures.
    antialiasing can be set to change how the texture looks when scaled. Default to nearest (pixelated)
    if the texture this uses has already been created, setting antialiasing to a non-none value will set it for everything using that texture

    set_image_from_buffer(self, image_name, ix, iy, image_buffer, keep_dim = False, display = True, antialiasing = None)
    Adds an image from a buffer. Passing the width, height, and pre-formatted buffer is required.
    Be sure to make image_name unique to prevent possible conflicts
    You may pass None for as image_name if you want the engine to dynamically create a unique name. (you cannot do this with set_image)
    keep_dim being set to true means that the width, height and texture dimension attributes will be unchanged from the previous image
    If display is set to false, the game won't attemt to draw the image.
    This is NOT the same as unsetting the show flag, since you won't be able to undo it.
    Setting display to false is for pre-loading textures.
    antialiasing can be set to change how the texture looks when scaled. Default to nearest (pixelated)
    if the texture this uses has already been created, setting antialiasing to a non-none value will set it for everything using that texture

    remove_image(self, keep_dim = False)
    Clears the image if it's already been set
    keep_dim being set to true means that the width, height and texture dimension attributes will be unaffected

    get_texture_dimensions(self)
    Returns the current image's texture dimensions
    If the image isn't set, returns None
    Also returns None with any other sort of error

    get_dimensions(self)
    Returns the width and height in [width, height] format
    Undefined values returned if no image set

    get_effective_dimensions(self)
    Returns the width and height after being modified by the size attribute in [width, height] format
    Undefined values returned if no image set

    set_antialiasing(self, val)
    Sets the antialiasing for the sprite's TEXTURE!
    Options are AA_NEAREST (fuzzy) and AA_LINEAR (pixilated)
    Note that the change will apply to ALL sprites that use this texture!

    destroy(self)
    Clears all data in preparation for deleting the sprite
    Does not actually delete the sprite. Use del for that (though it's good practice to call destroy before using del)


    (properties)

    update_image
    Flag to force it to update the VRAM with image data. True = force this frame

    layer
    Determines draw order for sprites. Should be a real number, though anything python can use comparisons on is fine
    Lower value = drawn sooner (further back).

    pos
    Determines draw position on the screen in pixels.
    [x,y] format

    offset
    Offsets the draw position on the screen in pixels.
    [x,y] format. Default [0,0]
    The size modifier treats this position as an origin point.

    other_offsets
    Dictionary of offsets that offset the draw position on the screen in pixels
    Values are in [x,y] format
    This is NOT treated as an origin point for the purposes of the size modifier
    Changing this directly does NOT set the update_image flag. Please use the change_offset() function instead.
    You may manually set the update_image flag after modifying this if you wish, but that's not recommended.

    width
    Width of the sprite in pixels
    The texture will be stretched/shrunk if changed. See tex_widths/tex_heights

    height
    Height of the sprite in pixels
    The texture will be stretched/shrunk if changed. See tex_widths/tex_heights

    tex_widths
    Determines where the texture will be drawn on the sprite's geometry.
    This value is a fraction (1.0 will be equivalent to the texture's length)
    [left,right] format. Default [0.0,1.0]
    Having values higher than 1.0 or lower than 0.0 will "tile" the sprite, though only do this with textures that have widths that are a multiple of 2

    tex_heights
    Determines where the texture will be drawn on the sprite's geometry.
    This value is a fraction (1.0 will be equivalent to the texture's length)
    [bottom,top] format. Default [0.0,1.0]
    Having values higher than 1.0 or lower than 0.0 will "tile" the sprite, though only do this with textures that have heights that are a multiple of 2

    size
    Enlarges/shrinks the sprite.
    [x,y] format. Default is [1.0, 1.0]
    Value is a multiplier. 1.0 will result in no change, 0.5 will halve the size, 2.0 will double the size
    The size change will be centered around the sprite's origin point. Normally this is 0,0 (bottom left of the sprite)
    Setting the center flag(s) or changing the offsets will change the origin point.
    A size key cannot be specified by using the property. It will default to the default key. Use setSize and get_size for other keys.

    color
    Colorizes the sprite.
    [red,green,blue] format. Default is [1.0,1.0,1.0]
    Values passed should be floats (0.0-1.0)
    1.0 will result in 100% colorization.
    This can only subtract color, not add it. You can't make something "redder" but you can remove green and blue so it appears to have a red tint

    alpha
    Can make a sprite translucent/transparent
    Value is a fraction (0.0-1.0)
    1.0 will result in being fully visible. 0.0 will be invisible
    For images that already have partial alpha as part of their texture, this can only make them MORE translucent/transparent, not less
    In such a case, translucency is multiplied (0.5 texture alpha and 0.5 alpha set here = 0.25 alpha total)

    show
    Flag whether to draw the sprite at all
    "invisible" sprites still take some processing time (though much less), so please delete things if you're not using them

    center
    Flags that determine whether the sprite should be centered.
    [x,y] format. Default is [False,False]
    Centering will essentially offset the sprite pos by half the image's width and height
    The size attribute will use the center (possibly offset) as an origin point to determine new verticies.

    flip
    Flags that determine whether the sprite should be flipped.
    [x,y] format. Default is [False,False]
    Flipping will flip the sprite's texture.


    (Read only properties. Do not modify directly)

    image_path
    The image's path and/or name, as passed to set_image or set_image_to_buffer
    Returns None if no texture set

    original_width
    The image texture's width, in pixels
    Returns 0 if no texture set

    original_height
    The image texture's height, in pixels
    Returns 0 if no texture set

    bottom_left_corner
    Returns the bottom left corner of a sprite, no matter what that might be

    destroyed
    Flag whether the destroy method has been called yet.
    If true, this sprite should not be used for any further purpose and ought to be cleaned up.



Constants:
(standard ones only; see individual constants files for implementation specific constants)

AA_LINEAR = 0
AA_NEAREST = 1
Antialiasing constants. Linear is a smooth transition between colors, while nearest is "pixilated"

VSYNC_DEFAULT = False
The default vsync setting if none is passed to the window initializaiton.
Vsync being set to true prevents "tearing" but is slower

"""
