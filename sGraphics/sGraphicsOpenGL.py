

#kai's attempt at a graphics engine

#things from sgraphics package
from kaiengine.sGraphics.constants.opengl import * #note: some imports are in the constants file that aren't here. Ex: ctypes
from kaiengine.sGraphics.shaders.opengl import getShader, getScreenShader
from kaiengine.sGraphics.shaders.opengl import _createSpriteShader, _createScreenShader
from kaiengine.sGraphics.shaders.opengl import _swapSpriteShader, _swapScreenShader
from kaiengine.sGraphics.shaders.opengl import SHADERS_AVAILABLE, OVERLAY_SHADER
from kaiengine.sGraphics.shaders.opengl import CURRENT_SHADER, CURRENT_SCREEN_SHADER
from kaiengine.sGraphics.cannotresizewindowerror import CannotResizeWindowError
from kaiengine.sGraphics.invalidscreenshotcoordinateserror import InvalidScreenshotCoordinatesError

#things from kaiengine specifically
from kaiengine.sDict import sDict
from kaiengine.objectdestroyederror import ObjectDestroyedError
from kaiengine.resource import loadResource, ResourceUnavailableError
from kaiengine.debug import debugMessage
from kaiengine.uidgen import generateUniqueID

#external things
from OpenGL.GL import glBufferSubData, glGenTextures, glTexParameterf
from OpenGL.GL import glDeleteBuffers, glBufferData, glBindTexture
from OpenGL.GL import glPixelStorei, glTexImage2D, glDeleteTextures, glDrawArrays
from OpenGL.GL import glReadPixels, glUseProgram, glEnableVertexAttribArray
from OpenGL.GL import glDisableVertexAttribArray, glVertexAttribPointer
from OpenGL.GL import glGenVertexArrays, glBindVertexArray, glGetAttribLocation
from OpenGL.GL import glUniformMatrix4fv, glGetUniformLocation, glUniform1f
from OpenGL.GL import glBlendFunc, glEnable, glGenFramebuffers, glBindFramebuffer
from OpenGL.GL import GLenum, glCheckFramebufferStatus, glFramebufferTexture2D
from OpenGL.GL import glDrawBuffers, glClear, glUniform2f
from OpenGL.error import GLError
from OpenGL.arrays import vbo as glvbo
from PIL import Image
from numpy import array, float32

#basic python stuff
import weakref
import copy
from math import floor
import moderngl_window as mglw
#import traceback
#import math

gameWindow = None

UNIFORM_FUNC = {"float": glUniform1f, "matrix4": glUniformMatrix4fv}

def createBasicSpriteShader(vertex_shader = None, fragment_shader = None, handle="default"):
    if not SHADERS_AVAILABLE: return
    if gameWindow is not None:
        raise RuntimeError("Shaders must be created before graphicsInit!")
    _createBasicSpriteShader(vertex_shader=vertex_shader, fragment_shader=fragment_shader, handle=handle)

def createSpriteShader(vertex_shader = None, fragment_shaders = None, handle="default"):
    if not SHADERS_AVAILABLE: return
    if gameWindow is not None:
        raise RuntimeError("Shaders must be created before graphicsInit!")
    _createSpriteShader(vertex_shader=vertex_shader, fragment_shaders=fragment_shaders, handle=handle)

def createBasicScreenShader(vertex_shader = None, fragment_shader = None, handle="default"):
    if not SHADERS_AVAILABLE: return
    if gameWindow is not None:
        raise RuntimeError("Shaders must be created before graphicsInit!")
    _createBasicScreenShader(vertex_shader=vertex_shader, fragment_shader=fragment_shader, handle=handle)

def createScreenShader(vertex_shader = None, fragment_shaders = None, handle="default"):
    if not SHADERS_AVAILABLE: return
    if gameWindow is not None:
        raise RuntimeError("Shaders must be created before graphicsInit!")
    _createScreenShader(vertex_shader=vertex_shader, fragment_shaders=fragment_shaders, handle=handle)

def swapSpriteShader(handle="default"):
    if not SHADERS_AVAILABLE: return
    _swapSpriteShader(handle=handle)
    gameWindow.setSpriteShader(getShader())

def swapScreenShader(handle="default"):
    if not SHADERS_AVAILABLE: return
    _swapScreenShader(handle=handle)
    gameWindow.setScreenShader(getScreenShader())

def graphicsInit(window_x, window_y):
    graphicsInitWindow(CreateWindow(window_x, window_y))

def graphicsInitWindow(window):
    global gameWindow
    gameWindow = window
    _GraphicsInit()

def _GraphicsInit():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    return

def getGameWindow():
    return gameWindow

def graphicsUpdate():
    if gameWindow is not None:
        gameWindow.graphics_update()

def fixColorValues(colors):
    return fixColorValuesFloats(colors)

def fixColorValuesFloats(colors):
    colors = list(copy.copy(colors))
    for i in range(len(colors)):
        if colors[i] > 1:
            colors[i] = 1
    return tuple(colors)

def fixColorValuesIntegers(colors):
    colors = list(copy.copy(colors))
    for i in range(len(colors)):
        if colors[i] < 1 or (colors[i] == 1.0 and type(colors[i]) is float):
            colors[i] = int(colors[i] * COLOR_BASE)
    return tuple(colors)

def getTextureDimensions(path):
    if gameWindow is not None:
        return gameWindow.get_texture_dimensions(path)
    else:
        return [0,0]

def setGlobalScaling(value):
    if gameWindow is not None:
        gameWindow.set_global_scaling(value)

def getGlobalScaling():
    if gameWindow is not None:
        return gameWindow.get_global_scaling()
    return -1 #error

def setCameraXY(x, y):
    if gameWindow is not None:
        gameWindow.set_camera_xy(x, y)

def getCameraXY(x, y):
    if gameWindow is not None:
        return gameWindow.get_camera_xy()
    return None #error

def getScreenResolution(screenIndex=None):
    #TODO: replace pyglet call (get_display)
    disp = get_display()
    if screenIndex:
        screen = disp.get_screens()[screenIndex]
    else:
        screen = disp.get_default_screen()
    return (screen.width, screen.height)

def registerUniform(uniform_name, uniform_type, initial_value=None):
    if not SHADERS_AVAILABLE: return
    gameWindow.registerUniform(uniform_name, uniform_type, initial_value)

def registerScreenUniform(uniform_name, uniform_type, initial_value=None):
    if not SHADERS_AVAILABLE: return
    gameWindow.registerScreenUniform(uniform_name, uniform_type, initial_value)

def setUniformValue(uniform_name, value):
    if not SHADERS_AVAILABLE: return
    gameWindow.setUniformValue(uniform_name, value)

def setScreenUniformValue(uniform_name, value):
    if not SHADERS_AVAILABLE: return
    gameWindow.setScreenUniformValue(uniform_name, value)

class sSprite(object):
    def __init__(self, image_path = None, antialiasing = None):
        if gameWindow is None:
            raise Exception("Sprite creation attempted before graphics engine initialization!")
        self._image_path = None
        self._index = None
        self._ihandler_appended = False
        self._destroyed = False

        #update flags
        self._update_image = False #true if update scheduled
        self._update_all = False #will update everything
        self._update_pos = False # will update pos
        self._update_tex = False # will update texture
        self._update_color = False # will update color
        self._update_flip = False # will update flip
        self._update_offsets = False # will update other offsets

        #old stuff for updates
        self._old_VBO_array = copy.copy(BASE_VBO_DATA)
        self._pos_error = [0.0, 0.0] #accumulating error for most things that affect verticies
        self._old_pos = [0,0]
        self._old_flip = False
        self._old_offsets = {}

        self.update_queue = []

        self._pos = [0,0]
        self._offset = [0,0]
        self.other_offsets = {}
        self._layer = 0
        self._width = 0
        self._height = 0
        self._tex_widths = TEX_COORD_BASIC_ARRAY
        self._tex_heights = TEX_COORD_BASIC_ARRAY
        self._original_width = 0
        self._original_height = 0
        self._size = sDict()
        self._size[DEFAULT_SIZE_KEY] = [1.0, 1.0]
        self._color = [1.,1.,1.]
        self._alpha = 1.
        self._show = True
        self._center = [False, False]
        self._flip = [False, False]


        if image_path is not None:
            self.set_image(image_path, antialiasing)

    @property
    def destroyed(self):
        return self._destroyed
    @destroyed.setter
    def destroyed(self, val):
        debugMessage("destroyed cannot be set outside of the destroy function")
    @property
    def image_path(self):
        return self.getImagePath()
    @image_path.setter
    def image_path(self, newvalue):
        debugMessage("image_path is read-only")
    @property
    def original_width(self):
        return self._original_width
    @original_width.setter
    def original_width(self, newvalue):
        debugMessage("original_width is read-only")
    @property
    def original_height(self):
        return self._original_height
    @original_height.setter
    def original_height(self, newvalue):
        debugMessage("original_height is read-only")
    @property
    def update_image(self):
        return self._update_image
    @update_image.setter
    def update_image(self, newvalue):
        self._setUpdateImage(newvalue)

    @property
    def layer(self):
        return self._layer
    @layer.setter
    def layer(self, newvalue):
        self.setLayer(newvalue)

    @property
    def pos(self):
        return self.getPos()
    @pos.setter
    def pos(self, newvalue):
        self.setPos(*newvalue)

    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, newvalue):
        self.setOffset(*newvalue)

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, newvalue):
        self.setWidth(newvalue)

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, newvalue):
        self.setHeight(newvalue)

    @property
    def tex_widths(self):
        return self._tex_widths
    @tex_widths.setter
    def tex_widths(self, newvalue):
        self.setTexWidths(*newvalue)

    @property
    def tex_heights(self):
        return self._tex_heights
    @tex_heights.setter
    def tex_heights(self, newvalue):
        self.setTexHeights(*newvalue)

    @property
    def size(self):
        return self.getSize()
    @size.setter
    def size(self, newvalue):
        self.setSize(*newvalue)

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, newvalue):
        self.setColor(*newvalue)

    @property
    def alpha(self):
        return self.getAlpha()
    @alpha.setter
    def alpha(self, newvalue):
        self.setAlpha(newvalue)

    @property
    def show(self):
        return self._show
    @show.setter
    def show(self, newvalue):
        self.setShow(newvalue)

    @property
    def center(self):
        return self._center
    @center.setter
    def center(self, newvalue):
        self.setCenter(*newvalue)

    @property
    def flip(self):
        return self._flip
    @flip.setter
    def flip(self, newvalue):
        self.setFlip(*newvalue)


    def _setUpdateImage(self, newvalue):
        if self.destroyed and newvalue:
            raise ObjectDestroyedError("modification of destroyed sprite attempted")
        if not self._ihandler_appended and newvalue and self._index is not None:
            try:
                gameWindow.appendIhandlerUpdate(self._index)
                self._ihandler_appended = True
            except AttributeError: #end of game error suppression:
                pass
        self._update_image = newvalue

    def setPos(self, x = None, y = None):
        newvalue = (float(x) if x is not None else self.pos[Xi], float(y) if y is not None else self.pos[Yi])
        if self._pos != newvalue:
            if not self._update_pos:
                self.update_image = True #updates pos only if appropriate
                self._old_pos = self._pos[:2]
                self._update_pos = True
                self._update_all = True
                self.update_queue.append(self.posVBOUpdate)
            self._pos = newvalue

    def getPos(self):
        return self._pos

    def setLayer(self, newvalue):
        if self._layer != newvalue:
            if self.destroyed:
                raise ObjectDestroyedError("modification of destroyed sprite attempted")
            self._layer = newvalue
            if self._index is not None and gameWindow is not None:
                gameWindow.move_image_layer(self._index, self.layer)

    def setOffset(self, x = None, y = None):
        newvalue = (x if x is not None else self.offset[Xi],y if y is not None else self.offset[Yi])
        if self._offset != newvalue:
            if not self._update_all:
                self.update_image = True
                self._update_all = True
            self._offset = newvalue

    def append_offset(self, x = 0, y = 0):
        key = generateUniqueID("SPRITE_APPENDED_OFFSET")
        self.change_offset(key, x, y)
        return key

    def remove_offset(self, index):
        try:
            if self.other_offsets[index] != [0,0]:
                self.update_image = True
            del self.other_offsets[index]
            del self._old_offsets[index]
        except KeyError:
            pass

    def change_offset(self, index, x = None, y = None):
        try:
            if x is None:
                x = self.other_offsets[index][Xi]
            if y is None:
                y = self.other_offsets[index][Yi]
            if [x,y] == self.other_offsets[index]:
                return
        except KeyError:
            if x is None:
                x = 0
            if y is None:
                y = 0
        if not self._update_offsets:
            self._old_offsets = {}
            self.update_image = True
            self._update_offsets = True
            self.update_queue.append(self.offsetsVBOUpdate)
        try: self._old_offsets[index] = self.other_offsets[index]
        except KeyError: self._old_offsets[index] = [0.0,0.0]
        self.other_offsets[index] = [x,y]

    def setWidth(self, newvalue):
        if self._width != newvalue:
            if not self._update_all:
                self.update_image = True
                self._update_all = True
            self._width = newvalue

    def setHeight(self, newvalue):
        if self._height != newvalue:
            if not self._update_all:
                self.update_image = True
                self._update_all = True
            self._height = newvalue

    def setDimensions(self, width = None, height = None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height

    def setTexWidths(self, x1 = None, x2 = None):
        newvalue = (float(x1) if x1 is not None else self._tex_widths[Xi], float(x2) if x2 is not None else self._tex_widths[Yi])
        if self._tex_widths != newvalue:
            self._tex_widths = newvalue
            if not self._update_tex:
                self.update_image = True
                self._update_tex = True
                self.update_queue.append(self.texVBOUpdate)

    def setTexHeights(self, y1 = None, y2 = None):
        newvalue = (float(y1) if y1 is not None else self._tex_heights[Xi], float(y2) if y2 is not None else self._tex_heights[Yi])
        if self._tex_heights != newvalue:
            self._tex_heights = newvalue
            if not self._update_tex:
                self.update_image = True
                self._update_tex = True
                self.update_queue.append(self.texVBOUpdate)

    def set_texture_dimensions(self, xLeft = None, xRight = None, yBottom = None, yTop = None):
        if xLeft is None:
            xLeft = self.tex_widths[LEFT]
        if xRight is None:
            xRight = self.tex_widths[RIGHT]
        if yBottom is None:
            yBottom = self.tex_heights[BOTTOM]
        if yTop is None:
            yTop = self.tex_heights[TOP]
        self.tex_widths = [xLeft, xRight]
        self.tex_heights = [yBottom, yTop]

    def tileTexture(self, xfactor = 1.0, yfactor = 1.0):
        current = self.get_effective_dimensions()
        targetDimensions = [current[0] / xfactor, current[1] / yfactor]
        self.set_texture_dimensions(0, targetDimensions[0], 0, targetDimensions[1])

    def crop(self, left, bottom, right, top):
        self.setSize((right-left)/(1.0*self.width), (top-bottom)/(1.0*self.height))
        self.set_texture_dimensions(left, right, bottom, top)

    def setSize(self, x = None, y = None, key = DEFAULT_SIZE_KEY):
        if key not in self._size.keys():
            self._size[key] = [1.0,1.0]
        if x is None:
            x = self._size[key][Xi]
        if y is None:
            y = self._size[key][Yi]
        if self._size[key] != [x,y]:
            if not self._update_all:
                self.update_image = True
                self._update_all = True
            self._size[key] = [x,y]


    def remove_size(self, key):
        try:
            del self._size[key]
            if not self._update_all:
                self.update_image = True
                self._update_all = True
        except KeyError:
            pass

    def getSize(self, key = DEFAULT_SIZE_KEY):
        return self._size.get(key, [1.0,1.0])

    def get_effective_size(self):
        returnval = [1.0,1.0]
        for size in self._size.values():
            returnval[Xi] *= size[Xi]
            returnval[Yi] *= size[Yi]
        return returnval

    def resetSize(self):
        for key in self._size.keys():
            self.remove_size(key)
        if not self._update_all:
            self.update_image = True
            self._update_all = True

    def setColor(self, r = None, g = None, b = None, alpha = None):
        #alpha setting is completely ignored
        newvalue = fixColorValues((r if r is not None else self.color[RED],
                   g if g is not None else self.color[GREEN],
                    b if b is not None else self.color[BLUE]))
        if self._color != newvalue:
            self._color = newvalue
            if not self._update_color:
                self.update_image = True
                self._update_color = True
                self.update_queue.append(self.colorVBOUpdate)

    def setAlpha(self, newvalue):
        if self._alpha != newvalue:
            self._alpha = newvalue
            if not self._update_color:
                self.update_image = True
                self._update_color = True
                self.update_queue.append(self.colorVBOUpdate)

    def getAlpha(self):
        return self._alpha

    def setShow(self, newvalue):
        if self._show != newvalue:
            self._show = newvalue
            if not self._update_all:
                self._update_all = True
                self.update_image = True

    def setCenter(self, x = None, y = None):
        newvalue = (x if x is not None else self.center[Xi], y if y is not None else self.center[Yi])
        if self._center != newvalue:
            if not self._update_all:
                self.update_image = True
                self._update_all = True
            self._center = newvalue

    def setFlip(self, x = None, y = None):
        newvalue = (x if x is not None else self.flip[Xi], y if y is not None else self.flip[Yi])
        if self._flip != newvalue:
            if not self._update_flip:
                self.update_image = True
                self._update_flip = True
                self._old_flip = self._flip[:]
                self.update_queue.append(self.flipVBOUpdate)
            self._flip = newvalue

    def set_image(self, image_path, tex_id = None, keep_dim = False, display = True, antialiasing = None):
        if gameWindow is not None:
            self.remove_image(keep_dim)
            self._index = gameWindow.add_image_handler(self, image_path, tex_id, display, antialiasing)
            self._ihandler_appended = False
            self._image_path = image_path
            sizes = gameWindow.get_texture_dimensions(self.image_path)
            self._original_width = sizes[Xi]
            self._original_height = sizes[Yi]
            if self.tex_widths == TEX_COORD_BASIC_ARRAY:
                self.tex_widths = [0., float(sizes[Xi])]
            if self.tex_heights == TEX_COORD_BASIC_ARRAY:
                self.tex_heights = [0., float(sizes[Yi])]
            if self.width == 0:
                self.width = sizes[Xi]
            if self.height == 0:
                self.height = sizes[Yi]
            self.update_image = True
            self._update_all = True

    def set_image_from_buffer(self, image_name, ix, iy, image_buffer, keep_dim = False, display = True, antialiasing = None):
        if gameWindow is not None:
            if image_name is None:
                image_name = gameWindow.get_unique_name()
            self.set_image(image_name, gameWindow.add_texture(image_name, ix, iy, image_buffer, antialiasing), keep_dim, display = display)

    def remove_image(self, keep_dim = False):
        if self.image_path is not None:
            if gameWindow is not None:
                gameWindow.remove_image_handler(self._index)
        self._index = None
        self._image_path = None
        self._original_width = 0
        self._original_height = 0
        if not keep_dim:
            self.width = 0
            self.height = 0
            if copy: #game close error suppression
                self.tex_widths = TEX_COORD_BASIC_ARRAY
                self.tex_heights = TEX_COORD_BASIC_ARRAY
            self.other_offsets.clear()

    def getImagePath(self):
        return self._image_path

    def get_texture_dimensions(self):
        if gameWindow and self.image_path is not None:
            return gameWindow.get_texture_dimensions(self.image_path)
        else:
            return None

    def getDimensions(self):
        return self.width, self.height

    get_dimensions = getDimensions #deprecated method name

    def getOriginalDimensions(self):
        return self.original_width, self.original_height

    def get_effective_dimensions(self):
        return self.width * self.get_effective_size()[0], self.height * self.get_effective_size()[1]

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getExtents(self):
        effective_size = self.get_effective_size()
        width = self.width * effective_size[Xi]
        height = self.height * effective_size[Yi]
        if self.center[Xi]:
            center_xoffset = width / 2
        else:
            center_xoffset = 0
        if self.center[Yi]:
            center_yoffset = height / 2
        else:
            center_yoffset = 0
        xoffset = self.offset[Xi] * effective_size[Xi]
        yoffset = self.offset[Yi] * effective_size[Yi]
        xleft = self.pos[Xi] + xoffset - center_xoffset
        xright = self.pos[Xi] + xoffset - center_xoffset + width
        ybottom = self.pos[Yi] + yoffset - center_yoffset
        ytop = self.pos[Yi] + yoffset - center_yoffset + height
        for key, offset in self.other_offsets.items():
            try:
                xleft += offset[Xi]
                xright += offset[Xi]
                ybottom += offset[Yi]
                ytop += offset[Yi]
            except TypeError:
                debugMessage("error with graphical offset. Key: " + key)
                self.other_offsets[key] = [0,0]
        return xleft, xright, ybottom, ytop

    def set_antialiasing(self, val):
        if gameWindow is not None and self.image_path is not None:
            gameWindow.set_texture_antialiasing(self.image_path, val)


    def update_vbo(self, vbo_offset):
        if not (self.original_width == 0 or self.original_height == 0) and gameWindow is not None:
            try:
                if self.show:
                    if True: #self._update_all:
                        self.mainVBOUpdate()
                        self._update_all = False #put here because I want it to be obvious that both update lists need to be updated as appropriate
                        self._update_pos = False #not doing a function call due to efficiency concerns
                        self._update_tex = False
                        self._update_color = False
                        self._update_flip = False
                        self._update_offsets = False
                    else:
                        for method in self.update_queue:
                            method()
                    self.update_queue = []
                else:
                    self._old_VBO_array = copy.copy(BASE_VBO_DATA)
                    self._update_all = False
                    self._update_pos = False
                    self._update_tex = False
                    self._update_color = False
                    self._update_flip = False
                    self._update_offsets = False
                gameWindow.get_vbo().bind()
                glBufferSubData(GL_ARRAY_BUFFER, vbo_offset * STRIDE_QUAD, STRIDE_QUAD,
                            array(self._old_VBO_array, dtype=float32))
                gameWindow.get_vbo().unbind()
            except:
                debugMessage(self.image_path)
                import traceback
                traceback.print_exc()
        self._update_image = False
        self._ihandler_appended = False

    def mainVBOUpdate(self):
        tex_left = self.tex_widths[LEFT] / self.original_width
        tex_right = self.tex_widths[RIGHT] / self.original_width
        tex_top = -self.tex_heights[TOP] / self.original_height
        tex_bottom = -self.tex_heights[BOTTOM] / self.original_height
        texture_array = [tex_left, tex_bottom, tex_right, tex_bottom, tex_left, tex_top,
                    tex_right, tex_top, tex_right, tex_bottom, tex_left, tex_top]
        xleft, xright, ybottom, ytop = self.getExtents()
        if self.flip[Xi]:
            xleft, xright = [xright, xleft]
        if self.flip[Yi]:
            ybottom, ytop = [ytop, ybottom]
        self._pos_error = [0.0,0.0] #reset accumulating error
        vertex_array = [xleft, ybottom, xright, ybottom, xleft, ytop,
                    xright, ytop, xright, ybottom, xleft, ytop]
        color_array = [self.color[RED],self.color[GREEN],self.color[BLUE],self.alpha]
        self._old_VBO_array = []
        for i in range(VERTEX_PER_TRIANGLE_PER_QUAD):
            self._old_VBO_array += texture_array[i*TEX_COORD_AMOUNT:i*TEX_COORD_AMOUNT + TEX_COORD_AMOUNT]
            self._old_VBO_array += vertex_array[i*VERTEX_COORD_AMOUNT:i*VERTEX_COORD_AMOUNT + VERTEX_COORD_AMOUNT]
            self._old_VBO_array += color_array
            self._old_VBO_array += [0.0]*16
        return

        #proposed change to this function

        tex_left = self.tex_widths[LEFT] / self.original_width
        tex_right = self.tex_widths[RIGHT] / self.original_width
        tex_top = -self.tex_heights[TOP] / self.original_height
        tex_bottom = -self.tex_heights[BOTTOM] / self.original_height
        if self.flip[Xi]:
            tex_left, tex_right = tex_right, tex_left
        if self.flip[Yi]:
            tex_top, tex_bottom = tex_bottom, tex_top
        texture_array = [tex_left, tex_bottom,
                         tex_right, tex_bottom,
                         tex_left, tex_top,
                         tex_right, tex_top,
                         tex_right, tex_bottom,
                         tex_left, tex_top]

        xoffset = self.offset[Xi]
        yoffset = self.offset[Yi]
        if self.center[Xi]:
            xoffset -= self.width / 2
        if self.center[Yi]:
            yoffset -= self.height / 2
        base_offsets = [xoffset, -yoffset,
                        self.width + xoffset, yoffset,
                        xoffset, self.height + yoffset,
                        self.width + xoffset, self.height + yoffset,
                        self.width + xoffset, yoffset,
                        xoffset, self.height + yoffset]

        xleft = 0
        xright = 0
        ybottom = 0
        ytop = 0
        for key, offset in self.other_offsets.items():
            try:
                xleft += offset[Xi]
                xright += offset[Xi]
                ybottom += offset[Yi]
                ytop += offset[Yi]
            except TypeError:
                debugMessage("error with graphical offset. Key: " + key)
                self.other_offsets[key] = [0,0]
        other_offsets = [xleft, ybottom,
                         xright, ybottom,
                         xleft, ytop,
                         xright, ytop,
                         xright, ybottom,
                         xleft, ytop]

        color_array = [self.color[RED],self.color[GREEN],self.color[BLUE],self.alpha]

        size_array = self.get_effective_size()

        self._old_VBO_array = []
        for i in range(VERTEX_PER_TRIANGLE_PER_QUAD):
            self._old_VBO_array += list(self.pos)
            self._old_VBO_array += base_offsets[i*VERTEX_COORD_AMOUNT:i*VERTEX_COORD_AMOUNT + VERTEX_COORD_AMOUNT]
            self._old_VBO_array += size_array
            self._old_VBO_array += other_offsets[i*VERTEX_COORD_AMOUNT:i*VERTEX_COORD_AMOUNT + VERTEX_COORD_AMOUNT]
            self._old_VBO_array += texture_array[i*TEX_COORD_AMOUNT:i*TEX_COORD_AMOUNT + TEX_COORD_AMOUNT]
            self._old_VBO_array += color_array
            self._old_VBO_array += [0.0]*16

    def posVBOUpdate(self):
        xshift = self.pos[Xi] - self._old_pos[Xi] + self._pos_error[Xi]
        yshift = self.pos[Yi] - self._old_pos[Yi] + self._pos_error[Yi]
        xshift_rounded = round(xshift)
        yshift_rounded = round(yshift)
        self._pos_error = [xshift - xshift_rounded, yshift - yshift_rounded]
        self._old_VBO_array[TEX_COORD_AMOUNT] += xshift_rounded #could make this a loop but unrolled for efficiency
        self._old_VBO_array[TEX_COORD_AMOUNT + 1] += yshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH + TEX_COORD_AMOUNT] += xshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH + TEX_COORD_AMOUNT + 1] += yshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*2 + TEX_COORD_AMOUNT] += xshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*2 + TEX_COORD_AMOUNT + 1] += yshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*3 + TEX_COORD_AMOUNT] += xshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*3 + TEX_COORD_AMOUNT + 1] += yshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*4 + TEX_COORD_AMOUNT] += xshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*4 + TEX_COORD_AMOUNT + 1] += yshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*5 + TEX_COORD_AMOUNT] += xshift_rounded
        self._old_VBO_array[SPRITE_VBO_LENGTH*5 + TEX_COORD_AMOUNT + 1] += yshift_rounded
        self._update_pos = False

    def texVBOUpdate(self):
        tex_left = self.tex_widths[LEFT] / self.original_width
        tex_right = self.tex_widths[RIGHT] / self.original_width
        tex_top = -self.tex_heights[TOP] / self.original_height
        tex_bottom = -self.tex_heights[BOTTOM] / self.original_height
        self._old_VBO_array[0] = tex_left
        self._old_VBO_array[1] = tex_bottom
        self._old_VBO_array[SPRITE_VBO_LENGTH] = tex_right
        self._old_VBO_array[SPRITE_VBO_LENGTH + 1] = tex_bottom
        self._old_VBO_array[SPRITE_VBO_LENGTH*2] = tex_left
        self._old_VBO_array[SPRITE_VBO_LENGTH*2 + 1] = tex_top
        self._old_VBO_array[SPRITE_VBO_LENGTH*3] = tex_right
        self._old_VBO_array[SPRITE_VBO_LENGTH*3 + 1] = tex_top
        self._old_VBO_array[SPRITE_VBO_LENGTH*4] = tex_right
        self._old_VBO_array[SPRITE_VBO_LENGTH*4 + 1] = tex_bottom
        self._old_VBO_array[SPRITE_VBO_LENGTH*5] = tex_left
        self._old_VBO_array[SPRITE_VBO_LENGTH*5 + 1] = tex_top
        self._update_tex = False

    def colorVBOUpdate(self):
        for i in range(VERTEX_PER_TRIANGLE_PER_QUAD):
            offset = i*SPRITE_VBO_LENGTH + VERTEX_TEX_LENGTH
            self._old_VBO_array[offset] = self.color[RED]
            self._old_VBO_array[offset + 1] = self.color[GREEN]
            self._old_VBO_array[offset + 2] = self.color[BLUE]
            self._old_VBO_array[offset + 3] = self.alpha
        self._update_color = False

    def flipVBOUpdate(self):
        #don't need to care about error in this one since it's already rounded
        if self._flip[0] != self._old_flip[0]:
            xleft = self._old_VBO_array[TEX_COORD_AMOUNT] #get the first vertex's x pos, since it's on the left
            xright = self._old_VBO_array[SPRITE_VBO_LENGTH + TEX_COORD_AMOUNT] # and the second's, sicne it's on the right
            self._old_VBO_array[TEX_COORD_AMOUNT] = xright
            self._old_VBO_array[SPRITE_VBO_LENGTH*2 + TEX_COORD_AMOUNT] = xright
            self._old_VBO_array[SPRITE_VBO_LENGTH*5 + TEX_COORD_AMOUNT] = xright
            self._old_VBO_array[SPRITE_VBO_LENGTH + TEX_COORD_AMOUNT] = xleft
            self._old_VBO_array[SPRITE_VBO_LENGTH*3 + TEX_COORD_AMOUNT] = xleft
            self._old_VBO_array[SPRITE_VBO_LENGTH*4 + TEX_COORD_AMOUNT] = xleft
        if self._flip[1] != self._old_flip[1]:
            ytop = self._old_VBO_array[SPRITE_VBO_LENGTH*2 + TEX_COORD_AMOUNT + 1]
            ybottom = self._old_VBO_array[TEX_COORD_AMOUNT + 1]
            self._old_VBO_array[TEX_COORD_AMOUNT + 1] = ytop
            self._old_VBO_array[SPRITE_VBO_LENGTH + TEX_COORD_AMOUNT + 1] = ytop
            self._old_VBO_array[SPRITE_VBO_LENGTH*4 + TEX_COORD_AMOUNT + 1] = ytop
            self._old_VBO_array[SPRITE_VBO_LENGTH*2 + TEX_COORD_AMOUNT + 1] = ybottom
            self._old_VBO_array[SPRITE_VBO_LENGTH*3 + TEX_COORD_AMOUNT + 1] = ybottom
            self._old_VBO_array[SPRITE_VBO_LENGTH*5 + TEX_COORD_AMOUNT + 1] = ybottom
        self._update_flip = False

    def offsetsVBOUpdate(self):
        xshift = 0.0
        yshift = 0.0
        for key, val in self._old_offsets.items():
            xshift += self.other_offsets[key][Xi] - val[Xi]
            yshift += self.other_offsets[key][Yi] - val[Yi]
        xshift += self._pos_error[Xi]
        yshift += self._pos_error[Yi]
        xshift_rounded = round(xshift)
        yshift_rounded = round(yshift)
        self._pos_error = [xshift - xshift_rounded, yshift - yshift_rounded]
        for i in range(VERTEX_PER_TRIANGLE_PER_QUAD):
            offset = i*SPRITE_VBO_LENGTH + TEX_COORD_AMOUNT
            self._old_VBO_array[offset] += xshift_rounded
            self._old_VBO_array[offset + 1] += yshift_rounded
        self._update_offsets = False

    def destroy(self):
        self._destroyed = True
        self.remove_image(True)
        self.update_queue = []

    def __del__(self):
        self.destroy()

class ImageHandler(object):
    def __init__(self, obj):
        self._owner = weakref.ref(obj)
        self.ihandler_index = None
        self._image_path = None
        self._image_index = None
        self._draw_index = None
        self._vbo_index = None
        self._vbo_offset = None
        self._tex_id = None
        self.layer = None
        self._add_image_flag = False
        self.removed = False

    @property
    def owner(self):
        try:
            return self._owner()
        except:
            return None
    @owner.setter
    def owner(self, newval):
        self._owner = weakref.ref(obj)
    @property
    def image_path(self):
        return self._image_path
    @image_path.setter
    def image_path(self, newval):
        self._image_path = newval
    @property
    def image_index(self):
        return self._image_index
    @image_index.setter
    def image_index(self, newval):
        self._image_index = newval
    @property
    def vbo_index(self):
        return self._vbo_index
    @vbo_index.setter
    def vbo_index(self, newval):
        self._vbo_index = newval
    @property
    def vbo_offset(self):
        return self._vbo_offset
    @vbo_offset.setter
    def vbo_offset(self, newval):
        self._vbo_offset = newval
    @property
    def draw_index(self):
        return self._draw_index
    @draw_index.setter
    def draw_index(self, newval):
        self._draw_index = newval
    @property
    def tex_id(self):
        return self._tex_id
    @tex_id.setter
    def tex_id(self, newval):
        self._tex_id = newval
    @property
    def add_image_flag(self):
        return self._add_image_flag
    @add_image_flag.setter
    def add_image_flag(self, newval):
        if newval:
            gameWindow.appendIhandlerAddImage(self.ihandler_index)
        self._add_image_flag = newval

    def set_ihandler_index(self, ihandler_index):
        self.ihandler_index = ihandler_index

    def set_data(self,image_path, tex_id,draw_index, add_image_flag, layer):
        self.image_path = image_path
        self.tex_id = tex_id
        self.image_index = None
        self.draw_index = draw_index
        self.vbo_index = None
        self.vbo_offset = None
        self.layer = layer
        self.add_image_flag = add_image_flag

    def remove_data(self):
        if gameWindow is not None:
            self.add_image_flag = False
            gameWindow.remove_texture(self.image_path)
            self.image_path = None
            self.tex_id = None
            gameWindow.remove_image(self.image_index, self.ihandler_index)
            self.image_index = None
            self.ihandler_index = None
            self.vbo_index = None
            self.vbo_offset = None
            gameWindow.remove_display_object(self.draw_index)
            self.draw_index = None
            self.layer = None
            self.set_removed()


    def move_layer(self, layer):
        if gameWindow is not None:
            if self.add_image_flag:
                self.layer = layer
            else:
                self.add_image_flag = True
                self.layer = layer

    def move_layer_without_change(self, layer):
        """moves layer without changing vram or anything. Careful calling this; must update the window's data too"""
        if self.image_index is not None:
            self.image_index[0] = layer
            self.layer = layer

    def force_update(self):
        if not self.removed:
            self.owner.update_image = True
            self.owner._update_all = True

    def check_update(self):
        if not self.removed and self.vbo_offset is not None:
            self.owner.update_vbo(self.vbo_offset + self.vbo_index)

    def check_add_image(self):
        if not self.removed:
            if self.image_index is not None:
                gameWindow.remove_image(self.image_index, self.ihandler_index)
            self.image_index, self.vbo_index, self.vbo_offset = gameWindow.add_image(self.tex_id, self.layer, self.ihandler_index)
            self.add_image_flag = False

    def set_removed(self):
        self.removed = True

    def destroy(self):
        self.remove_data()

    def __del__(self):
        self.destroy()

class windowVBOInterface(object):

    def vboInit(self):

        self.ihandlers = sDict()
        self.ihandlers_removelist = set()
        self.ihandlers_addimagelist = set()
        self.ihandlers_updatelist = set()
        self.imageupdate_refreshlist = set()
        self.imageupdate_sortlist = set()
        self.sorted_layer_keys = []
        self.layers_sorted = False
        self.images = sDict()
        self.graphic_data = {}
        self.objs = sDict()
        self.vbo = glvbo.VBO(array([], dtype='float32'))
        self.vbo_size = BASE_VBO_SIZE
        self.vbo_chunk_sizes = {}
        self.vbo_claims = 'f'*self.vbo_size
        self.name_counter = 0
        self.setup_vao()
        self.setup_vbo()
        self.setup_frame_vbo()
        self.setup_overlay_vbo()

    def setup_overlay_vbo(self):
        glBindVertexArray(self.overlay_vao)
        frame_data = array([-1.0, -1.0, -1.0, -1.0,
                             1.0, -1.0,  1.0, -1.0,
                            -1.0,  1.0, -1.0,  1.0,
                            -1.0,  1.0, -1.0,  1.0,
                             1.0, -1.0,  1.0, -1.0,
                             1.0,  1.0,  1.0,  1.0], dtype='float32')
        self.overlay_vbo = glvbo.VBO(frame_data)
        self.overlay_vbo.bind()

        index_tex = glGetAttribLocation(OVERLAY_SHADER, "tex")
        index_coord = glGetAttribLocation(OVERLAY_SHADER, "coord")
        glEnableVertexAttribArray(index_tex)
        glVertexAttribPointer(index_tex, TEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, 16, TEX_COORD_STRIDE_OFFSET)
        glEnableVertexAttribArray(index_coord)
        glVertexAttribPointer(index_coord, VERTEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, 16, VERTEX_STRIDE_OFFSET)

        glBufferData(GL_ARRAY_BUFFER,
                     96,
                     copy.copy(frame_data),
                     GL_STATIC_DRAW)

        glBindVertexArray(0)
        glDisableVertexAttribArray(index_tex)
        glDisableVertexAttribArray(index_coord)
        self.overlay_vbo.unbind()

    def setup_frame_vbo(self):
        glBindVertexArray(self.fbo_vao)
        frame_data = array([-1.0, -1.0, -1.0, -1.0,
                             1.0, -1.0,  1.0, -1.0,
                            -1.0,  1.0, -1.0,  1.0,
                            -1.0,  1.0, -1.0,  1.0,
                             1.0, -1.0,  1.0, -1.0,
                             1.0,  1.0,  1.0,  1.0], dtype='float32')
        self.frame_vbo = glvbo.VBO(frame_data)
        self.frame_vbo.bind()

        index_tex = glGetAttribLocation(self.post_shader, "tex")
        index_coord = glGetAttribLocation(self.post_shader, "coord")
        glEnableVertexAttribArray(index_tex)
        glVertexAttribPointer(index_tex, TEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, 16, TEX_COORD_STRIDE_OFFSET)
        glEnableVertexAttribArray(index_coord)
        glVertexAttribPointer(index_coord, VERTEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, 16, VERTEX_STRIDE_OFFSET)

        glBufferData(GL_ARRAY_BUFFER,
                     96,
                     copy.copy(frame_data),
                     GL_STATIC_DRAW)

        glBindVertexArray(0)
        glDisableVertexAttribArray(index_tex)
        glDisableVertexAttribArray(index_coord)
        self.frame_vbo.unbind()

    def refresh_screen_vao_pointers(self):
        glBindVertexArray(self.fbo_vao)
        self.frame_vbo.bind()

        index_tex = glGetAttribLocation(self.post_shader, "tex")
        index_coord = glGetAttribLocation(self.post_shader, "coord")
        glEnableVertexAttribArray(index_tex)
        glVertexAttribPointer(index_tex, TEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, 16, TEX_COORD_STRIDE_OFFSET)
        glEnableVertexAttribArray(index_coord)
        glVertexAttribPointer(index_coord, VERTEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, 16, VERTEX_STRIDE_OFFSET)

        glBindVertexArray(0)
        glDisableVertexAttribArray(index_tex)
        glDisableVertexAttribArray(index_coord)
        self.frame_vbo.unbind()

    def get_unique_name(self):
        name = UNIQUE_NAME_BASE + str(self.name_counter)
        self.name_counter += 1
        if name in self.graphic_data:
            return self.get_unique_name()
        return name

    def create_vbo_chunk(self, amount = 1):
        index = self.vbo_claims.find('f'*amount)
        if index == -1:
            self.expand_vbo()
            return self.create_vbo_chunk(amount)
        self.vbo_claims = self.vbo_claims[:index] + 't'*amount + self.vbo_claims[index+amount:]
        self.vbo_chunk_sizes[index] = amount
        return index

    def extend_vbo_chunk(self, index, amount = 1):
        if index in self.vbo_chunk_sizes:
            newsize = self.vbo_chunk_sizes[index] + amount
            self.vbo_claims = self.vbo_claims[:index] + 'f'*self.vbo_chunk_sizes[index] + self.vbo_claims[index+self.vbo_chunk_sizes[index]:]
            if self.vbo_claims[index:index+newsize] != 'f'*newsize:
                index2 = self.vbo_claims.find('f'*newsize)
                if index2 == -1:
                    self.expand_vbo()
                    return self.extend_vbo_chunk(index, amount)
            else:
                index2 = index
            self.vbo_claims = self.vbo_claims[:index2] + 't'*newsize + self.vbo_claims[index2+newsize:]
            del self.vbo_chunk_sizes[index]
            self.vbo_chunk_sizes[index2] = newsize
        else:
            index2 = self.create_vbo_chunk(amount)
        return index2

    def shrink_vbo_chunk(self, index, amount = 1):
        if index in self.vbo_chunk_sizes:
            oldsize = self.vbo_chunk_sizes[index]
            self.vbo_chunk_sizes[index] -= amount
            if self.vbo_chunk_sizes[index] < 0:
                self.vbo_chunk_sizes[index] = 0
            self.vbo_claims = self.vbo_claims[:index+self.vbo_chunk_sizes[index]] + 'f'*(oldsize-self.vbo_chunk_sizes[index]) + self.vbo_claims[index+oldsize:]
            if self.vbo_chunk_sizes[index] <= 0:
                del self.vbo_chunk_sizes[index]
                index = None
        else:
            index = None
        return index

    def removeVBOChunk(self, index):
        if index in self.vbo_chunk_sizes:
            self.vbo_claims = self.vbo_claims[:index] +'f'*self.vbo_chunk_sizes[index] + self.vbo_claims[index+self.vbo_chunk_sizes[index]:]
            del self.vbo_chunk_sizes[index]

    def expand_vbo(self):
        glDeleteBuffers(1, [self.vbo])
        old_size = self.vbo_size
        self.vbo_size *= VBO_RESIZE_MULTIPLIER
        self.vbo_claims = self.vbo_claims + 'f'*(self.vbo_size - old_size)
        self.vbo = glvbo.VBO(array([], dtype='float32'))
        self.setup_vbo()
        for ihandler in self.ihandlers.values():
            ihandler.force_update()

    def setup_vao(self):
        self.vao = glGenVertexArrays(1)
        self.fbo_vao = glGenVertexArrays(1)
        self.overlay_vao = glGenVertexArrays(1)

    def setup_vbo(self):
        glBindVertexArray(self.vao)
        self.vbo.bind()

        index_tex = glGetAttribLocation(self.shader, "tex")
        index_coord = glGetAttribLocation(self.shader, "coord")
        index_color = glGetAttribLocation(self.shader, "color")
        index_userdata = glGetAttribLocation(self.shader, "userdata")
        glEnableVertexAttribArray(index_tex)
        glVertexAttribPointer(index_tex, TEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, TEX_COORD_STRIDE_OFFSET)
        glEnableVertexAttribArray(index_coord)
        glVertexAttribPointer(index_coord, VERTEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, VERTEX_STRIDE_OFFSET)
        glEnableVertexAttribArray(index_color)
        glVertexAttribPointer(index_color, COLOR_VALUE_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, COLOR_STRIDE_OFFSET)
        if index_userdata != -1:
            glEnableVertexAttribArray(index_userdata)
            glVertexAttribPointer(index_userdata, USER_DATA_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, USER_DATA_STRIDE_OFFSET)

        glBufferData(GL_ARRAY_BUFFER,self.vbo_size*STRIDE_QUAD,array(copy.copy(BASE_VBO_DATA)*self.vbo_size,dtype=float32),GL_DYNAMIC_DRAW)

        glBindVertexArray(0)
        glDisableVertexAttribArray(index_tex)
        glDisableVertexAttribArray(index_coord)
        glDisableVertexAttribArray(index_color)
        if index_userdata != -1:
            glDisableVertexAttribArray(index_userdata)
        self.vbo.unbind()

    def refresh_sprite_vao_pointers(self):
        glBindVertexArray(self.vao)
        self.vbo.bind()

        index_tex = glGetAttribLocation(self.shader, "tex")
        index_coord = glGetAttribLocation(self.shader, "coord")
        index_color = glGetAttribLocation(self.shader, "color")
        index_userdata = glGetAttribLocation(self.shader, "userdata")
        glEnableVertexAttribArray(index_tex)
        glVertexAttribPointer(index_tex, TEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, TEX_COORD_STRIDE_OFFSET)
        glEnableVertexAttribArray(index_coord)
        glVertexAttribPointer(index_coord, VERTEX_COORD_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, VERTEX_STRIDE_OFFSET)
        glEnableVertexAttribArray(index_color)
        glVertexAttribPointer(index_color, COLOR_VALUE_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, COLOR_STRIDE_OFFSET)
        if index_userdata != -1:
            glEnableVertexAttribArray(index_userdata)
            glVertexAttribPointer(index_userdata, USER_DATA_AMOUNT, VALUE_TYPE, GL_FALSE, STRIDE, USER_DATA_STRIDE_OFFSET)

        glBindVertexArray(0)
        glDisableVertexAttribArray(index_tex)
        glDisableVertexAttribArray(index_coord)
        glDisableVertexAttribArray(index_color)
        if index_userdata != -1:
            glDisableVertexAttribArray(index_userdata)
        self.vbo.unbind()

    def add_image_handler(self, obj, path, texture_id = None, display = True, antialiasing = None):
        if texture_id is None:
            tex_id = self.add_texture(path, antialiasing)
        else:
            tex_id = texture_id
        index = self.ihandlers.append(ImageHandler(obj))
        self.ihandlers[index].set_ihandler_index(index)
        if display:
            add_image_flag = True
            draw_index = self.objs.append(weakref.ref(obj))
        else:
            add_image_flag = False
            draw_index = None
        self.ihandlers[index].set_data(path, tex_id, draw_index, add_image_flag, obj.layer)
        if antialiasing is not None:
            #to ensure we set antialiasing if texture already exists
            self.set_texture_antialiasing(path, antialiasing)
        return index

    def remove_display_object(self, obj_index):
        try:
            del self.objs[obj_index]
        except:
            pass

    def appendIhandlerAddImage(self, index):
        self.ihandlers_addimagelist.add(index)

    def appendIhandlerUpdate(self, index):
        self.ihandlers_updatelist.add(index)

    def appendImageUpdateRefresh(self, index, imageset):
        key = (index, imageset)
        self.imageupdate_refreshlist.add(key)

    def appendImageUpdateSort(self, index, imageset):
        key = (index, imageset)
        self.imageupdate_sortlist.add(key)

    def checkImageUpdateChange(self, oldindex, newindex):
        for imageset in self.images[newindex].keys():
            oldkey = (oldindex, imageset)
            newkey = (newindex, imageset)
            try:
                self.imageupdate_refreshlist.remove(oldkey)
            except KeyError:
                pass
            else:
                self.imageupdate_refreshlist.add(newkey)
            try:
                self.imageupdate_sortlist.remove(oldkey)
            except KeyError:
                pass
            else:
                self.imageupdate_sortlist.add(newkey)

    def remove_image_handler(self, index):
        if index in self.ihandlers:
            self.ihandlers_removelist.add(index)
            self.ihandlers[index].set_removed()

    def delete_image_handler(self, index):
        try:
            self.ihandlers[index].destroy()
            del self.ihandlers[index]
        except KeyError:
            pass

    def add_texture(self, image_path, ix = None, iy = None, image_data = None, antialiasing = None):
        if image_path not in self.graphic_data:
            if image_data is None:
                texture, dim, image_data = loadImage(image_path, antialiasing)
            else:
                texture, dim = loadImageFromBuffer(ix, iy, image_data, antialiasing)
            self.graphic_data[image_path] = {}
            self.graphic_data[image_path][COUNT] = 1
            self.graphic_data[image_path][TEXTURES] = texture
            self.graphic_data[image_path][IMAGE_DATA] = image_data
            self.graphic_data[image_path][DIM] = dim
        else:
            self.graphic_data[image_path][COUNT] += 1
        return self.graphic_data[image_path][TEXTURES]

    def loadImageData(self, image_path):
        if image_path in self.graphic_data:
            x, y = self.graphic_data[image_path][DIM]
            return x, y, self.graphic_data[image_path][IMAGE_DATA]
        else:
            if PNG_EXTENSION not in image_path: #TODO: make this not necessary somehow
                image_path += PNG_EXTENSION
            im = Image.open(loadResource(image_path))
            return [im.size[0], im.size[1], im.convert("RGBA")]

    def remove_texture(self, image_path):
        if image_path in self.graphic_data:
            self.graphic_data[image_path][COUNT] -= 1
            if self.graphic_data[image_path][COUNT] <= 0:
                freeImage(self.graphic_data[image_path][TEXTURES])
                del self.graphic_data[image_path]

    def get_texture_dimensions(self, image_path):
        try:
            return self.graphic_data[image_path][DIM]
        except KeyError:
            try:
                ix, iy, image = self.loadImageData(image_path)
                return [ix,iy]
            except:
                debugMessage("failed getting texture dimensions for " + str(image_path) + ". If you're using a buffer, did you be sure to turn it into a texture first?")
                return [0,0]

    def set_texture_antialiasing(self, image_path, antialiasing):
        if image_path in self.graphic_data:
            antialiasing = interpretAntialiasing(antialiasing)
            glBindTexture(GL_TEXTURE_2D, self.graphic_data[image_path][TEXTURES])
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, antialiasing)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, antialiasing)

    def add_image(self, tex_id, layer, ihandler_index):
        '''Do not call outside of graphics_update'''
        #adds an image to the draw list by tex id and layer, and then returns an index to it in [layer, index] format
        if layer not in self.images:
            self.images[layer] = sDict()
            self.layers_sorted = False
        newtexture = True
        for key in self.images[layer]:
            if self.images[layer][key][IMAGE_TEXTURE] == tex_id:
                newtexture = False
                layer_index = key
                self.images[layer][key][IMAGE_COUNT] += 1
                if self.images[layer][key][IMAGE_COUNT] >= self.images[layer][key][IMAGE_SPACE]:
                    vbo_index = self.extend_vbo_chunk(self.images[layer][key][IMAGE_VBO], self.images[layer][key][IMAGE_COUNT]) #conveniently nearly doubles it every time
                    self.images[layer][key][IMAGE_SPACE] += self.images[layer][key][IMAGE_COUNT]
                else:
                    vbo_index = self.images[layer][key][IMAGE_VBO]
                if vbo_index == self.images[layer][key][IMAGE_VBO]:
                    self.ihandlers[ihandler_index].force_update()
                else:
                    self.images[layer][key][IMAGE_VBO] = vbo_index
                    self.appendImageUpdateRefresh(layer, key)
                    self.appendImageUpdateSort(layer, key)
                self.images[layer][key][IMAGE_IHANDLER].append(ihandler_index)
                vbo_offset = self.images[layer][key][IMAGE_COUNT] - 1
                break
        if newtexture:
            vbo_index = self.create_vbo_chunk(IMAGE_SPACE_DEFAULT)
            self.images[layer].append([tex_id, vbo_index, 1, [], IMAGE_SPACE_DEFAULT]) #texture ID, VBO index, count, ihandler_indexes, available space
            self.images[layer].last_item()[IMAGE_IHANDLER].append(ihandler_index)
            vbo_offset = 0
            layer_index = self.images[layer].length() - 1
            self.appendImageUpdateRefresh(layer, layer_index)
        index = [layer, layer_index]
        return [index, vbo_index, vbo_offset]

    def remove_image(self, img_pos, ihandler_index):
        """Do not call outside of graphics_update"""
        if img_pos is not None and ihandler_index is not None:
            try:
                try:
                    delete_key = self.images[img_pos[0]][img_pos[1]][IMAGE_IHANDLER].index(ihandler_index)
                except:
                    return True
                self.images[img_pos[0]][img_pos[1]][IMAGE_COUNT] -= 1
                del self.images[img_pos[0]][img_pos[1]][IMAGE_IHANDLER][delete_key]
                if self.images[img_pos[0]][img_pos[1]][IMAGE_COUNT] <= 0:
                    self.removeVBOChunk(self.images[img_pos[0]][img_pos[1]][IMAGE_VBO])
                    del self.images[img_pos[0]][img_pos[1]]
                    if len(self.images[img_pos[0]]) < 1: #remove empty layer
                        del self.images[img_pos[0]]
                        self.layers_sorted = False
                else:
                    self.appendImageUpdateSort(img_pos[0], img_pos[1])
            except:
                import traceback
                traceback.print_exc()
        return False

    def move_image_layer(self, ihandler_index, new_layer):
        if self.ihandlers[ihandler_index].add_image_flag:
            self.ihandlers[ihandler_index].move_layer(new_layer)
        else:
            oldlayer = self.ihandlers[ihandler_index].image_index[0]
            if oldlayer not in self.images:
                return
            if len(self.images[oldlayer].values()) > 1 or new_layer in self.images or self.images[oldlayer].last_item()[IMAGE_COUNT] > 1:
                self.ihandlers[ihandler_index].move_layer(new_layer)
            else: #hackish special case for images who are the sole residents of a layer moving to a new layer:
                self.images[new_layer] = self.images[oldlayer]
                del self.images[oldlayer]
                self.ihandlers[ihandler_index].move_layer_without_change(new_layer)
                self.layers_sorted = False
                self.checkImageUpdateChange(oldlayer, new_layer)


    def clear_all_images(self):
        removal_list = []
        for layer in self.images:
            for index in self.images[layer]:
                removal_list.append([layer, index])
        for index in removal_list:
            self.remove_image(index)
        self.images.clear()
        self.raws = {}

    def get_image_data(self, index):
        try:
            return self.images[index[0]][index[1]]
        except:
            return None

    def get_vbo(self):
        return self.vbo


#TODO: replace pyglet call (Window)
class sWindow(mglw.WindowConfig, windowVBOInterface):

    gl_version = (3, 3)

    def __init__(self, width=800, height=600, vsync = VSYNC_DEFAULT, fullscreen=False, fake_fullscreen=False):
        if fake_fullscreen:
            super(sWindow, self).__init__(width=width, height=height, vsync = vsync, resizable=False, style=Window.WINDOW_STYLE_BORDERLESS)
        else:
            super(sWindow, self).__init__(width=width, height=height, vsync = vsync, fullscreen=fullscreen, resizable=False)
        self.fbo_texture = None
        self.overlay_fbo_texture = None
        self._fbos = {}
        self._fbohandle = None
        self._draw_overlay = True
        self.global_scaling = 1
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.time = 0.0
        self.shaderInit()
        self.fboInit()
        self.vboInit()
        self.overlayInit()
        self.uniforms = {}
        self.uniform_values = {}
        self.screen_uniforms = {}
        self.screen_uniform_values = {}
        self.registerUniform("orthom", "matrix4")
        self.registerUniform("time", "float", 0.0)
        self.updateMatrix()

    def shaderInit(self):
        self.shader = getShader()
        self.post_shader = getScreenShader()

    def setSpriteShader(self, shader):
        if self.shader == shader: return
        self.shader = shader
        self.refresh_sprite_vao_pointers()

    def setScreenShader(self, shader):
        if self.post_shader == shader: return
        self.post_shader = shader
        self.fboInit()
        self.refresh_screen_vao_pointers()

    @property
    def fbo(self):
        return self._fbos[self._fbohandle]

    def makeFBO(self, handle):
        if handle not in self._fbos:
            self._fbos[handle] = glGenFramebuffers(1)

    def fboInit(self):
        handle = CURRENT_SCREEN_SHADER
        self._fbohandle = handle
        self.makeFBO(handle)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        if not self.fbo_texture:
            self.fbo_texture = glGenTextures(1)
            self._fbo_tex_size = tuple(self.get_size())
            glBindTexture(GL_TEXTURE_2D, self.fbo_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.get_size()[0], self.get_size()[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        else:
            glBindTexture(GL_TEXTURE_2D, self.fbo_texture)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.fbo_texture, 0)

        draw_buffers = GLenum(GL_COLOR_ATTACHMENT0)
        glDrawBuffers(1, draw_buffers)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Couldn't initialize framebuffer correctly!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def updateFBOSize(self, width, height):
        if self._fbo_tex_size == (width, height): return
        self._fbo_tex_size = (width, height)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glDeleteTextures(self.fbo_texture)
        self.fbo_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.fbo_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.fbo_texture, 0)
        draw_buffers = GLenum(GL_COLOR_ATTACHMENT0)
        glDrawBuffers(1, draw_buffers)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Couldn't initialize framebuffer correctly!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def overlayInit(self):
        self.overlay_fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.overlay_fbo)
        if not self.overlay_fbo_texture:
            self.overlay_fbo_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.overlay_fbo_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.get_size()[0], self.get_size()[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        else:
            glBindTexture(GL_TEXTURE_2D, self.overlay_fbo_texture)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.overlay_fbo_texture, 0)

        draw_buffers = GLenum(GL_COLOR_ATTACHMENT0)
        glDrawBuffers(1, draw_buffers)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Couldn't initialize framebuffer correctly!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def on_draw(self):
        return
        #self._main_draw_function()

    def flip(self, *args, **kwargs):
        return #booya

    def graphics_update(self):
        self.uniform_values["time"] += 0.01667
        for index in self.ihandlers_addimagelist: #add new images, if needed
            self.ihandlers[index].check_add_image()
        self.ihandlers_addimagelist.clear()
        for index in self.ihandlers_removelist: #only remove the data here, don't remove the ihandler from the list yet
            self.ihandlers[index].remove_data() #this removes old images
        self.vbo.bind()
        for layer, imageset_index in self.imageupdate_refreshlist:#if needed, refresh the VBO area in vram to base values:
            try:
                imageset = self.images[layer][imageset_index]
            except KeyError:
                continue
            tempvals = array(BASE_VBO_DATA*imageset[IMAGE_COUNT], dtype=float32)
            glBufferSubData(GL_ARRAY_BUFFER, imageset[IMAGE_VBO] * STRIDE_QUAD, STRIDE_QUAD * imageset[IMAGE_COUNT], tempvals)
            for index in imageset[IMAGE_IHANDLER]: #and of course force things to update their vbo area
                self.ihandlers[index].force_update()
        self.imageupdate_refreshlist.clear()
        self.vbo.unbind()
        for layer, imageset_index in self.imageupdate_sortlist: #also do any offset sorting if needed:
            try:
                imageset = self.images[layer][imageset_index]
            except KeyError:
                continue
            counter = 0
            for ihandler_index in imageset[IMAGE_IHANDLER]:
                self.ihandlers[ihandler_index].vbo_index = imageset[IMAGE_VBO]
                if self.ihandlers[ihandler_index].vbo_offset != counter:
                    self.ihandlers[ihandler_index].vbo_offset = counter
                    self.ihandlers[ihandler_index].force_update()
                counter += 1
        self.imageupdate_sortlist.clear()
        '''if len(self.ihandlers_updatelist) > 0:
            print len(self.ihandlers_updatelist)
            print "---"'''
        for index in self.ihandlers_updatelist: #do any vbo updates that are needed
                self.ihandlers[index].check_update()
        self.ihandlers_updatelist.clear()
        for index in self.ihandlers_removelist: #now we completely delete the ihandlers
            self.delete_image_handler(index)
        self.ihandlers_removelist.clear()
        self._main_draw_function()

    def getUniformArgs(self, uniform_name, uniform_type):
        if uniform_type == "float":
            return (self.uniform_values[uniform_name],)
        elif "matrix" in uniform_type:
            return (1, GL_FALSE, self.uniform_values[uniform_name])

    def getScreenUniformArgs(self, uniform_name, uniform_type):
        if uniform_type == "float":
            return (self.screen_uniform_values[uniform_name],)
        elif "matrix" in uniform_type:
            return (1, GL_FALSE, self.screen_uniform_values[uniform_name])

    def registerUniform(self, uniform_name, uniform_type, initial_value=None):
        self.uniforms[uniform_name] = uniform_type
        self.uniform_values[uniform_name] = initial_value

    def registerScreenUniform(self, uniform_name, uniform_type, initial_value=None):
        self.screen_uniforms[uniform_name] = uniform_type
        self.screen_uniform_values[uniform_name] = initial_value

    def setUniformValue(self, uniform_name, value):
        self.uniform_values[uniform_name] = value

    def setScreenUniformValue(self, uniform_name, value):
        self.screen_uniform_values[uniform_name] = value

    def _drawToFBO(self, _glBindTexture=glBindTexture, _glDrawArrays=glDrawArrays, _glUniform1f=glUniform1f, _glGetUniformLocation=glGetUniformLocation, _getUniformArgs=getUniformArgs):
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        if not self.layers_sorted:
            self.sorted_layer_keys = sorted(self.images.keys())
            self.layers_sorted = True
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for uniform_name, uniform_type in self.uniforms.items():
            loc = _glGetUniformLocation(self.shader, uniform_name)
            UNIFORM_FUNC[uniform_type](loc, *_getUniformArgs(self, uniform_name, uniform_type))
        glBindVertexArray(self.vao)
        _layer = glGetUniformLocation(self.shader, "layer")
        _img = None
        for layer in self.sorted_layer_keys:
            _glUniform1f(_layer, layer)
            for image in self.images[layer].values():
                if _img != (_img := image[IMAGE_TEXTURE]):
                    _glBindTexture(GL_TEXTURE_2D, _img)
                _glDrawArrays(GL_TRIANGLES, image[IMAGE_VBO]*VERTEX_PER_TRIANGLE_PER_QUAD, image[IMAGE_COUNT]*VERTEX_PER_TRIANGLE_PER_QUAD)

    def _drawFBOtoScreen(self):
        glUseProgram(self.post_shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for uniform_name, uniform_type in self.screen_uniforms.items():
            loc = glGetUniformLocation(self.post_shader, uniform_name)
            UNIFORM_FUNC[uniform_type](loc, *self.getScreenUniformArgs(uniform_name, uniform_type))
        loc = glGetUniformLocation(self.post_shader, "scaling")
        glUniform2f(loc, self.global_scaling, self.global_scaling)
        loc = glGetUniformLocation(self.post_shader, "step")
        glUniform2f(loc, *self.step)
        loc = glGetUniformLocation(self.post_shader, "time")
        glUniform1f(loc, self.uniform_values["time"])
        glBindVertexArray(self.fbo_vao)
        glBindTexture(GL_TEXTURE_2D, self.fbo_texture)
        glDrawArrays(GL_TRIANGLES, 0, 6)

    def _drawOverlay(self):
        glUseProgram(OVERLAY_SHADER)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindVertexArray(self.overlay_vao)
        glBindTexture(GL_TEXTURE_2D, self.overlay_fbo_texture)
        glDrawArrays(GL_TRIANGLES, 0, 6)

    def _main_draw_function(self):
        #main draw function
        try:
            windowsize = self.get_size()
            if windowsize[Xi] <= 0 or windowsize[Yi] <= 0: #crash prevention on minimize
                return
            self._drawToFBO()
            self._drawFBOtoScreen()
            if self._draw_overlay:
                self._drawOverlay()
            super(sWindow, self).flip()
        except GLError:
            #TODO: possibly only suppress during close?
            pass

    def set_global_scaling(self, value):
        self.global_scaling = value
        self.updateMatrix()

    def get_global_scaling(self):
        return self.global_scaling

    def set_camera_xy(self, x, y):
        self.camera_x = float(x)
        self.camera_y = float(y)
        self.updateMatrix()

    def get_camera_xy(self):
        return self.camera_x, self.camera_y

    def get_largest_screen_size(self):
        #TODO: replace pyglet call (get_display)
        widths, heights = tuple(zip(*[(screen.width, screen.height) for screen in get_display().get_screens()]))
        return (max(widths), max(heights))

    def updateMatrix(self):
        width, height = self.get_size()

        left = floor(self.camera_x + 0.0001) #fix floating point errors causing jittering
        right = left + width
        bottom = floor(self.camera_y + 0.0001)
        top = bottom + height
        self.orthoMatrix = array([2.0/width, 0, 0, -1.0*((right+left)/width),
                                  0, 2.0/height, 0, -1.0*((top+bottom)/height),
                                  0, 0, -1.0, 0,
                                  0, 0, 0, 1.0])
        self.step = (1.0/width, 1.0/height)
        self.setUniformValue("orthom", self.orthoMatrix)
        self.updateFBOSize(width, height)

    def set_dimensions(self, width, height, skipCheck=False, forceSize=False):
        """redirect this to the pyglet function"""
        oldSize = self.get_size()
        maxWidth, maxHeight = self.get_largest_screen_size()
        if not forceSize and (maxHeight < height or maxWidth < width):
            raise CannotResizeWindowError
        if not self.fullscreen:
            self.set_size(int(width), int(height))
        if skipCheck:
            self.updateMatrix()
            return
        if not self.get_size() == (width, height):
            self.set_size(*oldSize)
            self.updateMatrix()
            raise CannotResizeWindowError
        self.updateMatrix()

def createWindow(width, height):
    return sWindow(width=width, height=height)

def loadImageData(*args, **kwargs):
    return getGameWindow().loadImageData(*args, **kwargs)

def loadImage(image_path, antialiasing):
    ix, iy, image = loadImageData(image_path)
    texture, dim = loadImageFromBuffer(ix, iy, image, antialiasing)
    return texture, dim, image
    #silly thing that shows boundaries of sprites. comment out above return line to activate
    im = Image.new('RGBA',(ix,iy),(255,255,255,48))
    im.paste(image,(0,0),image)
    texture, dim = loadImageFromBuffer(ix, iy, im, antialiasing)
    return texture, dim, im

def loadImageFromBuffer(ix, iy, image_data, antialiasing):
    antialiasing = interpretAntialiasing(antialiasing)
    ID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, ID)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, antialiasing)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, antialiasing)
    glTexImage2D(GL_TEXTURE_2D, 0, 4, ix, iy, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, array(image_data, 'B'))
    return [ID, [ix, iy]]

def freeImage(image_ID):
    try:
        glDeleteTextures(image_ID)
    except TypeError:
        pass

def interpretAntialiasing(antialiasing):
    if antialiasing == AA_NEAREST:
        return GL_NEAREST
    elif antialiasing == AA_LINEAR:
        return GL_LINEAR
    return GL_NEAREST #default to nearest

def takeScreenshot(left=0, right=None, bottom=0, top=None, ignoreScaling=False, normalizeScale=False, palette=False):
    size = getGameWindow().get_size()

    if ignoreScaling:
        scaling = 1
    else:
        scaling = getGlobalScaling()

    left *= scaling
    bottom *= scaling

    if right is None:
        width = size[0] - left
    else:
        right *= scaling
        width = right - left
    if top is None:
        height = size[1] - bottom
    else:
        top *= scaling
        height = top - bottom

    if (width <= 0 or left+width > size[0] or left < 0 or
        height <= 0 or bottom+height > size[1] or bottom < 0):
            raise InvalidScreenshotCoordinatesError("Coordinates %s %s %s %s did not resolve to a valid window rect." % (left, right, bottom, top))

    buff = glReadPixels(left, bottom, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    screenshot = Image.frombytes(mode="RGB", size=(int(width), int(height)), data=buff)
    screenshot = screenshot.transpose(Image.FLIP_TOP_BOTTOM)
    if palette:
        screenshot = screenshot.convert(mode="P", dither=None, palette=Image.ADAPTIVE)

    if normalizeScale:
        screenshot = screenshot.resize(width/scaling, height/scaling)

    return screenshot
