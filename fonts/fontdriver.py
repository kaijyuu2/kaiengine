

import os

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from numpy import array

from kaiengine.sGraphics import fixColorValuesIntegers, loadImageData
from kaiengine.sGraphics.constants import *
from kaiengine import sGraphics
from kaiengine import load
from kaiengine import display
from kaiengine.resource import loadResource, ResourceUnavailableError, toStringPath
from kaiengine.debug import debugMessage
from kaiengine.uidgen import generateUniqueID

from kaiengine.gconfig import *

from . import fontglobals

GFONT2_UID = "_graphical_font_2_"
GFONT3_UID = "_graphical_font_3_"

class Font(object):
    def __init__(self, path = None):
        self.path = path

    def get_width(self, text, font_size):
        debugMessage("get_width function not overwritten for " + str(self.path) + "; returning 0")
        return 0

    def get_height(self, font_size):
        debugMessage("get_height function not overwritten for " + str(self.path) + "; returning 0")
        return 0

    def get_dim(self, text, font_size):
        return [self.get_width(text, font_size), self.get_height(font_size)]

    def text_to_image(self, text, font_size):
        return display.CreateTextLabel(text, font_size, self.path)

    def get_default_size(self):
        return MENU_TEXT_SIZE

    def destroy(self):
        pass

    def __del__(self):
        self.destroy()

class GraphicFont3(Font):
    def __init__(self, path = None):
        super().__init__(path)
        self.glyphs_path = None
        self.glyphs = None
        self.glyph_data = {}
        self.glyph_size = [1,1]
        self.standard_glyph_width = 1
        self.standard_glyph_height = 1
        self.default_char_pos = (0,0)
        self.loaded_string_paths = {}
        self.loaded_strings = {}
        self.default_size = DEFAULT_GRAPHICAL_FONT_SIZE
        self.font_folder = None
        self.antialiasing = AA_NEAREST

        self.load_prop()
        self.load_graphics()

    def get_width(self, text, size):
        total_width = 0
        for glyph in self.get_glyph_list(text):
            try: total_width += self.glyph_data[glyph].get(GFONT3_GLYPH_WIDTH, self.standard_glyph_width-1)
            except KeyError: total_width += self.standard_glyph_width-1
        return int(float(total_width) * size / self.default_size)

    def get_height(self, size):
        return int(float(self.standard_glyph_height) * size / self.default_size)

    def load_prop(self):
        if self.path is not None:
            prop = load.loadGraphicFont3Data(self.path)
            if GFONT_FOLDER in prop:
                self.font_folder = prop[GFONT_FOLDER]
            if GFONT_DEFAULT_SIZE in prop:
                self.default_size = prop[GFONT_DEFAULT_SIZE]
            if GFONT_FOLDER_GLYPHS in prop:
                self.glyph_data.update(prop[GFONT_FOLDER_GLYPHS])
            if GFONT_ANTIALIASING in prop:
                if prop[GFONT_ANTIALIASING].lower() == "linear":
                    self.antialiasing = AA_LINEAR
                elif prop[GFONT_ANTIALIASING].lower() == "nearest":
                    self.antialiasing = AA_NEAREST
            self.glyph_size = prop.get(GFONT3_SIZE, [1,1])
            self.default_char_pos = prop.get(GFONT3_DEFAULT_CHAR_POS, (0,0))
            

    def load_graphics(self):
        if self.font_folder is None:
            glyphfilepath = os.path.splitext(self.path)[0] + PNG_EXTENSION
        else:
            glyphfilepath = fontglobals.getFontPath(self.font_folder)
        if self.glyphs is not None:
            self.glyphs.destroy()
        self.glyphs = display.createSpritePlaceholder(None, self.antialiasing)
        self.glyphs.set_image(glyphfilepath)
        self.glyphs_path = glyphfilepath
        self.standard_glyph_width = int((self.glyphs.width-1) / self.glyph_size[0])
        self.standard_glyph_height = int((self.glyphs.height-1) / self.glyph_size[1])

    def get_glyph_list(self, text):
        keyslist = []
        for char in text:
            if char in self.glyph_data:
                keyslist.append(char)
            else:
                keyslist.append(GRAPHICAL_FONT_DEFAULT_CHAR)
        return keyslist

    def text_to_image(self, text, size = None):
        try:
            return self.loaded_string_paths[text]
        except KeyError:
            texpath = generateUniqueID(GFONT3_UID)
            self.loaded_string_paths[text] = texpath
            self.loaded_strings[text] = display.createSpritePlaceholder(None, self.antialiasing)
            self.loaded_strings[text].set_image_from_buffer(texpath, *self.text_to_image_buffer(text))
            return texpath

    def text_to_image_buffer(self, text, size = None):
        truesize = (max(self.get_width(text, self.default_size), 1) + 2, self.get_height(self.default_size) + 2)
        im = Image.new('RGBA',truesize,(0,0,0,0))
        xpos = 0
        im3 = loadImageData(self.glyphs_path)[2]
        for glyph in self.get_glyph_list(text):
            glyph_data = self.glyph_data.get(glyph, {})
            xcrop, ycrop = glyph_data.get(GFONT3_GLYPH_POS, self.default_char_pos)
            startx = xcrop * self.standard_glyph_width
            starty = ycrop * self.standard_glyph_height
            x = glyph_data.get(GFONT3_GLYPH_WIDTH, self.standard_glyph_width+1)
            y = glyph_data.get(GFONT3_GLYPH_HEIGHT, self.standard_glyph_height+1)
            im2 = im3.crop((startx, starty,startx + x, starty + y))
            im.paste(im2, (xpos,truesize[1] - y), im2)
            xpos += x-2 #pixel border
        return truesize[0], truesize[1], im.convert("RGBA")

class GraphicFont2(Font):
    def __init__(self, path = None):
        super(GraphicFont2, self).__init__(path)
        self.glyphs = {}
        self.loaded_string_paths = {}
        self.loaded_strings = {}
        self.standard_height = 0
        self.default_size = DEFAULT_GRAPHICAL_FONT_SIZE
        self.font_folder = None
        self.antialiasing = AA_NEAREST

        self.load_prop()
        self.load_graphics()

    def get_width(self, text, size):
        total_width = 0
        for glyph in self.get_glyph_list(text):
            total_width += self.glyphs[glyph].width
        return int(float(total_width) * size / self.default_size)

    def get_height(self, size):
        return int(float(self.standard_height) * size / self.default_size)

    def load_prop(self):
        if self.path is not None:
            prop = load.loadGraphicFont2Data(self.path)
            if GFONT_FOLDER in prop:
                self.font_folder = prop[GFONT_FOLDER]
            if GFONT_DEFAULT_SIZE in prop:
                self.default_size = prop[GFONT_DEFAULT_SIZE]
            if GFONT_FOLDER_GLYPHS in prop:
                for key, val in prop[GFONT_FOLDER_GLYPHS].items():
                    self.set_glyph(key, val)
            if GFONT_ANTIALIASING in prop:
                if prop[GFONT_ANTIALIASING].lower() == "linear":
                    self.antialiasing = AA_LINEAR
                elif prop[GFONT_ANTIALIASING].lower() == "nearest":
                    self.antialiasing = AA_NEAREST

    def load_graphics(self):
        if self.font_folder is None:
            glyphfilepath = toStringPath(*FULL_FONT_PATH)
        else:
            glyphfilepath = fontglobals.getFontPath(self.font_folder)
        glyphs = load.load_graphic_font_glyph_paths(glyphfilepath)
        for glyph in glyphs:
            key = os.path.splitext(os.path.basename(glyph))[0]
            if key not in self.glyphs:
                self.set_glyph(key, glyph, True)
        for key, val in GRAPHICAL_FONT_DEFAULT_GLYPHS.items():
            if key not in self.glyphs.keys():
                if key == GRAPHICAL_FONT_DEFAULT_CHAR and not fontglobals.checkGlyphExists(val):
                    #TODO: Handle this better, by including the default char image elsewhere, or making algorithmically, or something.
                    raise Exception("Graphical Font Error: Default character does not exist! Make sure a file named \"defaultchar.png\" exists in the font directory.")
                self.set_glyph(key, val, True)
        glyphlist = [glyph for key, glyph in self.glyphs.items() if key not in GRAPHICAL_FONT_DEFAULT_GLYPHS]
        if len(glyphlist) > 0:
            self.standard_height = max([glyph.height for glyph in glyphlist])
        else:
            self.standard_height = self.glyphs[GRAPHICAL_FONT_DEFAULT_CHAR].height

    def set_glyph(self, key, val, direct_path = False):
        if self.font_folder is None or direct_path:
            val = fontglobals.getFontPath(val)
        else:
            val = fontglobals.getFontPath(self.font_folder, val)
        if fontglobals.checkGlyphExists(val):
            self.glyphs[key] = GraphicFontGlyph(val)

    def get_glyph_list(self, text):
        keyslist = []
        for char in text:
            if char in self.glyphs:
                keyslist.append(char)
            else:
                keyslist.append(GRAPHICAL_FONT_DEFAULT_CHAR)
        return keyslist

    def text_to_image(self, text, size = None):
        try:
            return self.loaded_string_paths[text]
        except KeyError:
            texpath = generateUniqueID(GFONT2_UID)
            self.loaded_string_paths[text] = texpath
            self.loaded_strings[text] = display.createSpritePlaceholder(None, self.antialiasing)
            self.loaded_strings[text].set_image_from_buffer(texpath, *self.text_to_image_buffer(text))
            return texpath

    def text_to_image_buffer(self, text, size = None):
        truesize = (max(self.get_width(text, self.default_size), 1) + 2, self.get_height(self.default_size) + 2)
        im = Image.new('RGBA',truesize,(0,0,0,0))
        xpos = 0
        for glyph in self.get_glyph_list(text):
            x, y, im2 = loadImageData(self.glyphs[glyph].get_full_path())
            im.paste(im2, (xpos,truesize[1] - y), im2)
            xpos += x-2 #pixel border
        return truesize[0], truesize[1], im.convert("RGBA")

class GraphicFontGlyph(object):
    def __init__(self, path):
        self.path = path
        x,y = sGraphics.getTextureDimensions(self.get_full_path())
        self.width = x - 2  #-2 for the pixel border
        self.height = y - 2

    def get_full_path(self):
        return fontglobals.getFontPath(self.path)

    def destroy(self):
        pass

    def __del__(self):
        self.destroy()

class GraphicFont(Font):
    def __init__(self, path = None):
        super(GraphicFont, self).__init__(path)
        self.glyphs = {}
        self.loaded_glyphs = {}
        self.standard_height = 0
        self.default_size = DEFAULT_GRAPHICAL_FONT_SIZE
        self.font_folder = None
        self.antialiasing = AA_NEAREST

        self.load_prop()
        self.load_graphics()

    def load_prop(self):
        if self.path is not None:
            prop = load.load_graphic_font_data(self.path)
            if GFONT_FOLDER in prop:
                self.font_folder = prop[GFONT_FOLDER]
            if GFONT_DEFAULT_SIZE in prop:
                self.default_size = prop[GFONT_DEFAULT_SIZE]
            if GFONT_FOLDER_GLYPHS in prop:
                for key, val in list(prop[GFONT_FOLDER_GLYPHS].items()):
                    self.set_glyph(key, val)
            if GFONT_ANTIALIASING in prop:
                if prop[GFONT_ANTIALIASING].lower() == "linear":
                    self.antialiasing = AA_LINEAR
                elif prop[GFONT_ANTIALIASING].lower() == "nearest":
                    self.antialiasing = AA_NEAREST



    def load_graphics(self):
        if self.font_folder is None:
            glyphfilepath = toStringPath(*FULL_FONT_PATH)
        else:
            glyphfilepath = fontglobals.getFontPath(self.font_folder)
        glyphs = load.load_graphic_font_glyph_paths(glyphfilepath)
        for glyph in glyphs:
            key = os.path.splitext(os.path.basename(glyph))[0]
            if key not in list(self.glyphs.keys()):
                self.set_glyph(key, glyph, True)
        for key, val in list(GRAPHICAL_FONT_DEFAULT_GLYPHS.items()):
            if key not in list(self.glyphs.keys()):
                if key == GRAPHICAL_FONT_DEFAULT_CHAR and not fontglobals.checkGlyphExists(val):
                    #TODO: Handle this better, by including the default char image elsewhere, or making algorithmically, or something.
                    raise Exception("Graphical Font Error: Default character does not exist! Make sure a file named \"defaultchar.png\" exists in the font directory.")
                self.set_glyph(key, val, True)
        glyphlist = [glyph for key, glyph in list(self.glyphs.items()) if key not in list(GRAPHICAL_FONT_DEFAULT_GLYPHS.keys())]
        if len(glyphlist) > 0:
            self.standard_height = glyphlist[0].height
        else:
            self.standard_height = self.glyphs[GRAPHICAL_FONT_DEFAULT_CHAR].height
        self.pre_load_glyphs()

    def pre_load_glyphs(self):
        self.remove_loaded_glyphs()
        for key, glyph in list(self.glyphs.items()):
            self.loaded_glyphs[key] = display.createSpritePlaceholder(glyph.get_full_path(), self.antialiasing)

    def remove_loaded_glyphs(self):
        for glyph in list(self.loaded_glyphs.values()):
            glyph.destroy()
        self.loaded_glyphs = {}

    def set_glyph(self, key, val, direct_path = False):
        if self.font_folder is None or direct_path:
            val = fontglobals.getFontPath(val)
        else:
            val = fontglobals.getFontPath(self.font_folder, val)
        if fontglobals.checkGlyphExists(val):
            self.glyphs[key] = GraphicFontGlyph(val)


    def get_glyph_list(self, text):
        keyslist = []
        for char in text:
            if char in self.glyphs:
                keyslist.append(char)
            else:
                keyslist.append(GRAPHICAL_FONT_DEFAULT_CHAR)
        return keyslist

    def get_sprite_list(self, text, font_size):
        returnedlist = []
        for glyph in self.get_glyph_list(text):
            returnedlist.append(self.get_sprite_from_glyph(glyph, font_size))
        return returnedlist

    def get_sprite_from_glyph(self, glyph, font_size):
        sprite = display.createBarebonesSprite(self.glyphs[glyph].get_full_path())
        newsize = float(font_size) / self.default_size
        sprite.setSize(newsize, newsize)
        set_pixel_border(sprite)
        return sprite

    def get_width(self, text, font_size):
        text_glyphs = self.get_glyph_list(text)
        total_width = 0
        for glyph in text_glyphs:
            total_width += int(float(self.glyphs[glyph].width) * font_size / self.default_size)
        return total_width

    def get_height(self, font_size):
        return int(float(self.standard_height) * font_size / self.default_size)

    def get_default_size(self):
        return self.default_size

    def text_to_image_buffer(self, text, font_size):
        debugMessage("text_to_image_buffer not supported for graphical fonts. Path: " + str(self.path) + "; returning None")
        return 0, 0, None

    def destroy(self):
        if GraphicFont is not None:
            super(GraphicFont, self).destroy()
        self.remove_loaded_glyphs()
        for glyph in list(self.glyphs.values()):
            glyph.destroy()
        self.glyphs = {}

class TTFFont(Font):
    #yes I know about the redundancy in the name
    def __init__(self, path = None, font_size = None):
        super(TTFFont, self).__init__(path)
        self.font_sizes = {}
        self.check_font_size_exists(font_size)


    def check_font_size_exists(self, font_size):
        if font_size is not None and font_size not in self.font_sizes:
            self.create_font_size(font_size)

    def create_font_size(self, font_size):
        if self.path is not None:
            try:
                self.font_sizes[font_size] = ImageFont.truetype(loadResource(self.path), font_size)
            except ResourceUnavailableError:
                debugMessage("WARNING: Could not create font size due to resource error: %s" % self.path)
                raise ResourceUnavailableError

    def get_width(self, text, font_size):
        self.check_font_size_exists(font_size)
        return self.font_sizes[font_size].getsize(text)[0]

    def get_height(self, font_size):
        self.check_font_size_exists(font_size)
        return sum(self.font_sizes[font_size].getmetrics())

    def text_to_image_buffer(self, text, font_size, bordered, borderInverse, borderColor):
        #TODO: implement border color -- requires splitting label into two images (borders and main)
        font_size = int(font_size) #ensure int
        self.check_font_size_exists(font_size)
        truesize = (max(self.get_width(text, font_size), 1), self.get_height(font_size))
        im = Image.new('RGBA',truesize,(0,0,0,0))
        draw = ImageDraw.Draw(im)
        if bordered:
            if borderInverse:
                borderColor = COLOR_BLACK
            borderColor = fixColorValuesIntegers(borderColor)
            for xoffset in (-1, 1):
                for yoffset in (-1, 1):
                    draw.text((xoffset, yoffset), text, font=self.font_sizes[font_size], fill=borderColor)
        draw.text((0, 0), text, font=self.font_sizes[font_size], fill=DEFAULT_TEXT_FILL_COLOR)
        return truesize[0], truesize[1], array(im.convert("RGBA"), 'B')


class FontDriver(object):
    def __init__(self):
        self.fonts = {}


    def add_font(self, font_path, font_size = None):
        font_path = fontglobals.getFontPath(font_path)
        if font_path not in self.fonts:
            if TTF_EXTENSION == os.path.splitext(font_path)[1]:
                if font_size is None:
                    font_size = MENU_TEXT_SIZE
                self.fonts[font_path] = TTFFont(font_path, font_size)
                return
            if GRAPHIC_FONT_EXTENSION == os.path.splitext(font_path)[1]:
                self.fonts[font_path] = GraphicFont(font_path)
                return
            if GRAPHIC_FONT_2_EXTENSION == os.path.splitext(font_path)[1]:
                self.fonts[font_path] = GraphicFont2(font_path)
                return
            if GRAPHIC_FONT_3_EXTENSION == os.path.splitext(font_path)[1]:
                self.fonts[font_path] = GraphicFont3(font_path)
                return
            debugMessage("Font not found: " + font_path)
            debugMessage("Did you remember to include the extension?")

    def get_width(self, text, font_size, font_path):
        font_path = fontglobals.getFontPath(font_path)
        if font_path in self.fonts:
            return self.fonts[font_path].get_width(text, font_size)
        return 0

    def get_height(self, font_size, font_path):
        font_path = fontglobals.getFontPath(font_path)
        if font_path in self.fonts:
            return self.fonts[font_path].get_height(font_size)
        return 0

    def get_dim(self, text, font_size, font_path):
        return [self.get_width(text, font_size, font_path), self.get_height(font_size, font_path)]

    def text_to_image(self, text, font_size, font_path):
        font_path = fontglobals.getFontPath(font_path)
        if font_path not in self.fonts:
            self.add_font(font_path, font_size)
        return self.fonts[font_path].text_to_image(text, font_size)

    def text_to_image_buffer(self, text, font_size, font_path, bordered, borderInverse, borderColor):
        font_path = fontglobals.getFontPath(font_path)
        if font_path not in self.fonts:
            self.add_font(font_path, font_size)
        return self.fonts[font_path].text_to_image_buffer(text, font_size, bordered, borderInverse, borderColor)

    def get_sprite_list(self, text, font_path, font_size):
        font_path = fontglobals.getFontPath(font_path)
        if font_path not in self.fonts:
            self.add_font(font_path)
        return self.fonts[font_path].get_sprite_list(text, font_size)

    def get_default_font_size(self, font_path):
        font_path = fontglobals.getFontPath(font_path)
        if font_path not in self.fonts:
            self.add_font(font_path)
        return self.fonts[font_path].get_default_size()

    def destroy(self):
        for font in list(self.fonts.values()):
            font.destroy()
        self.fonts = {}

    def __del__(self):
        self.destroy()


def set_pixel_border(sprite): #set one pixel border. Don't call multiple times
    sprite.set_texture_dimensions(sprite.tex_widths[0] + 1, sprite.tex_widths[1] - 1, sprite.tex_heights[0] + 1, sprite.tex_heights[1] - 1)
    sprite.set_dimensions(sprite.width -2, sprite.height -2)
