

#main window stuff
from .sGraphics import sWindow
from pyglet.gl import *
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
        self.set_caption(settings.getValue(DYNAMIC_SETTINGS_GAME_CAPTION))
        self.test_timer = timer.Timer()

    def on_close(self):
        #do something on window close here
        event.gameCloseEvent()
        self.close()

    def set_icon(self, *images):
        from pyglet.image import load
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

    def on_key_press(self, symbol, modifiers):
        event.keyPressEvent(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        event.keyReleaseEvent(symbol, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        event.mousePressEvent(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        event.mouseReleaseEvent(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        event.mouseDragEvent(x, y, dx, dy, buttons, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        event.mouseMoveEvent(x, y, dx, dy)
        
    def on_mouse_enter(self, x, y):
        event.mouseEnterEvent(x, y)

    def on_mouse_leave(self, x, y):
        event.mouseExitEvent(x, y)

    def on_activate(self, *args, **kwargs):
        if self._fake_fullscreen:
           self.maximize()

    def on_deactivate(self, *args, **kwargs):
        if self._fake_fullscreen:
            self.minimize()

    def on_joybutton_release(self, joystick, button):
        pass
