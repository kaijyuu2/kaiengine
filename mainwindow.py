

#main window stuff
from .sGraphics import sWindow
from PIL import Image
from . import event
from .resource import toStringPath
from . import timer
import zipfile
from .debug import debugMessage
from kaiengine import settings

from sys import platform

from kaiengine.resource import loadResource, ResourceUnavailableError
from kaiengine.gconfig import *

class main_window(sWindow):

    def __init__(self, width=800, height=600, fullscreen=None, fake_fullscreen=None):
        super(main_window, self).__init__(width=width, height=height, vsync=settings.getValue(DYNAMIC_SETTINGS_VSYNC), fullscreen=fullscreen or settings.getValue(DYNAMIC_SETTINGS_FULLSCREEN), fake_fullscreen=fake_fullscreen or settings.getValue(DYNAMIC_SETTINGS_FAKE_FULLSCREEN))
        self._fake_fullscreen = fake_fullscreen
        #self.set_caption(settings.getValue(DYNAMIC_SETTINGS_GAME_CAPTION))
        self.resize_func = self.test_resize_func
        self.iconify_func = self.test_iconify_func
        self.key_event_func = self.test_key_event_func
        self.mouse_position_event_func = self.test_mouse_position_event_func
        self.mouse_drag_event_func = self.test_mouse_drag_event_func
        self.mouse_scroll_event_func = self.test_mouse_scroll_event_func
        self.mouse_press_event_func = self.test_mouse_press_event_func
        self.mouse_release_event_func = self.test_mouse_release_event_func
        self.unicode_char_entered_func = self.test_unicode_char_entered_func

    def dispatch_events(self, *args, **kwargs):
        #TODO: do we need this?
        pass

    def close(self):
        #do something on window close here
        event.gameCloseEvent()

    def set_icon(self, *images):
        #TODO: replace pyglet call (load)
        icons = []
        for image in images:
            try:
                icon_path = toStringPath(RESOURCE_PATH, MISC_DIR, image)
                data = loadResource(icon_path)
                im = load(icon_path, file=data)
            except:
                debugMessage("Error loading icon: %s" % image)
            else:
                icons.append(im)
        if len(icons) < 1:
            debugMessage("Couldn't load any program icons!")
            return False
        super().set_icon(*icons)

    def test_key_event_func(self, key, action, modifiers):
        if action == self.keys.ACTION_PRESS:
            event.keyPressEvent(key)
        else:
            event.keyReleaseEvent(key)

    def test_resize_func(self, width, height):
        print("window resize: ", width, height)

    def test_iconify_func(self, iconified):
        print("minimize/restore: ", iconified)

    def test_mouse_position_event_func(self, x, y, dx, dy):
        scaling = settings.getValue(DYNAMIC_SETTINGS_GLOBAL_SCALING)
        x = int(x / scaling)
        y = int(y / scaling)
        dx = int(dx / scaling)
        dy = int(dy / scaling)
        event.mouseMoveEvent(x, y, dx, dy)

    def test_mouse_drag_event_func(self, x, y, dx, dy):
        scaling = settings.getValue(DYNAMIC_SETTINGS_GLOBAL_SCALING)
        x = int(x / scaling)
        y = int(y / scaling)
        dx = int(dx / scaling)
        dy = int(dy / scaling)
        event.mouseMoveEvent(x, y, dx, dy)
        #event.mouseDragEvent(x, y, dx, dy, BUTTON) #TODO: buttons

    def test_mouse_scroll_event_func(self, x_offset, y_offset):
        print("mouse scroll: ", x_offset, y_offset)

    def test_mouse_press_event_func(self, x, y, button):
        scaling = settings.getValue(DYNAMIC_SETTINGS_GLOBAL_SCALING)
        x = int(x / scaling)
        y = int(y / scaling)
        print("Mouse press: ", x, y, button)
        event.mousePressEvent(x, y, button)

    def test_mouse_release_event_func(self, x, y, button):
        scaling = settings.getValue(DYNAMIC_SETTINGS_GLOBAL_SCALING)
        x = int(x / scaling)
        y = int(y / scaling)
        event.mouseReleaseEvent(x, y, button)

    def test_unicode_char_entered_func(self, character):
        print("unicode character entered: ", character)
