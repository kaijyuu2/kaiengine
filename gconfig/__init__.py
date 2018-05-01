
#default constants for the base engine. Feel free to overwrite


from kaiengine.othernone import OTHER_NONE

from .paths import *
from .datakeys import *
from .colors import *
from .settingskeys import *
from .eventkeys import *
from .interfacekaiconfig import *
from .defaultresources import *
from .default_keybinds import *
from .layers import *

#offset keys
CAMERA_KEY = "CAMERA"


SUPPORTED_FONTS = [TTF_EXTENSION, GRAPHIC_FONT_EXTENSION, GRAPHIC_FONT_2_EXTENSION, GRAPHIC_FONT_3_EXTENSION] #add more extensions if new font types are allowed


#text constants
DEFAULT_TEXT_SIZE = 30
MENU_TEXT_SIZE = DEFAULT_TEXT_SIZE #backwards compatibility
GIANT_TEXT_SIZE = 50
MENU_TEXT_COLOR = COLOR_BLACK
DEFAULT_TEXT_COLOR = COLOR_WHITE
TTF_TEXT_SIZE_KEY = "_TTF_SIZE_MOD"

#defaults for fonts
DEFAULT_GRAPHICAL_FONT_SIZE = 30
DEFAULT_TEXT_FILL_COLOR = (255,255,255)
DEFAULT_FONT = PFENNIG_FONT


#sprite hardcoded keys
SPRITE_PROP = "PROPERTIES"
SPRITE_DEFAULT_ANI_KEY = "DEFAULT" #if no default animation set, try to use an animation keyed "DEFAULT" if it exists
SPRITE_ANIMATION_FRAMES = "FRAMES"
SPRITE_ANIMATION_REPEAT = "REPEAT"
SPRITE_ANIMATION_FREEZE = "FREEZE"
SPRITE_ANIMATION_NEXT = "NEXT"
SPRITE_ANIMATION_FLAGS = "FLAGS"

#property names
FRAME_ANIMATION = "frame"
TIME_ANIMATION = "time"
SHEET_PROPORTIONAL = "proportional"
SHEET_ABSOLUTE = "absolute"


#animation keys
ANIMATION_DEFAULT = "DEFAULT"
ANIMATION_IDLE = "IDLE"

#filename for default ani in a folder
DEFAULT_FOLDER_ANI = "_DEFAULT"

#for looking up sprite graphics, should include folder and the like
GPATH = "_gpath"
#key for graphic_interface children to determine if they use glow sprites or not
GRAPHIC_INTERFACE_GLOWABLE = "_glowable"

#for graphical fonts; the defaults
GRAPHICAL_FONT_DEFAULT_CHAR = "_DEFAULT_CHAR"
GRAPHICAL_FONT_DEFAULT_CHAR_FILENAME = "defaultchar.png"

GRAPHICAL_FONT_DEFAULT_GLYPHS = {GRAPHICAL_FONT_DEFAULT_CHAR:GRAPHICAL_FONT_DEFAULT_CHAR_FILENAME}

#camera
CAMERA_SCROLL_BUFFER = 50


#object class type key
CLASS_TYPE = "_TYPE"
DEFAULT_CLASS_TYPE = "_DEFAULT" #value for the above CLASS_TYPE if none specified
#key to determine if loading failed
FAILED_LOAD_KEY = "_FAILED_LOAD"
ADDED_CLASS_TYPE = "_CLASS_TYPE_ADDED"
#key for getting additional properties from other files
PROP_KEY = "_PROP"
#metadata; to be ignored
META_KEY = "_META"
#file path stuff of an object
FILENAME = "_filename" #doesn't include extension
FILE_EXTENSION = "_fileextension" #extension of the loaded object
FILEPATH = "_filepath" #list format
#error string to check against to determine if a property in an object instance is undefined
PROP_UNDEFINED = "_PROPERTY_UNDEFINED_"


FADE_LAYER = 900001


#unusual default for when None or -1 isn't appropriate
DEFAULT_KWARG = OTHER_NONE
