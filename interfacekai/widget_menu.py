

from .interfaceWidget import InterfaceWidget
from .widget_label import LabelWidget

from kaiengine.resource import toStringPath
from kaiengine.keybinds import keyMatches
from kaiengine.debug import debugMessage

from kaiengine.gconfig import *

import operator, copy

#TODO: mouse input

DEFAULT_MENU_LAYOUT_OFFSET = [8,4]
DEFAULT_EXTRA_SPACE = [4,4]

class MenuWidgetHelper(InterfaceWidget):
    def __init__(self,owner, index, button_type = LabelWidget, border_spacing = DEFAULT_MENU_LAYOUT_OFFSET, *args, **kwargs):
        super(MenuWidgetHelper, self).__init__(owner, index, *args, **kwargs)
        self.setLayoutOffset(*border_spacing)
        self.button_spacer = tuple(DEFAULT_EXTRA_SPACE)
        self.button_type = button_type
        self.button_methods = {}
        self.button_args = {}
        self.button_kwargs = {}
        self._button_font = DEFAULT_FONT
        self.fixed_dimensions = False
        self.layout_center = (False, False)
        self._createLayoutButtons()

    def setFixedDimensions(self, val):
        if self.fixed_dimensions != val:
            self.fixed_dimensions = val
            self._updateDimensions()

    def getFixedDimensions(self):
        return self.fixed_dimensions

    def setButtonSpacer(self, x = None, y = None):
        if x is None: x = self.button_spacer[0]
        if y is None: y = self.button_spacer[1]
        self.button_spacer = (x,y)

    def setButtonType(self, button_type, replace_all = False):
        self.button_type = button_type
        if replace_all:
            for key, widget in list(self.widgets.items()):
                if type(widget) != button_type:
                    self.replaceButton(key, button_type)

    def replaceButton(self, index, button_type, *args, **kwargs):
        try: self.widgets[index].destroy()
        except KeyError: pass
        self.addWidget(button_type, index, *args, **kwargs)

    def setButtonMethod(self, key, method, *args, **kwargs):
        self.button_methods[key] = method
        self.button_args[key] = args
        self.button_kwargs[key] = kwargs

    def setButtonText(self, key, *args, **kwargs):
        self.widgets[key].setText(*args, **kwargs)

    def setButtonColor(self, key, *args, **kwargs):
        self.widgets[key].setSpriteColor(*args, **kwargs)

    def setButtonFont(self, font, *args, **kwargs):
        self._button_font = font
        for button in list(self.widgets.values()):
            try: button.setFont(font, *args, **kwargs)
            except AttributeError: pass

    def removeButtonMethod(self, key):
        try: del self.button_methods[key]
        except KeyError: pass
        try: del self.button_args[key]
        except KeyError: pass
        try: del self.button_kwargs[key]
        except KeyError: pass

    def removeAllButtonMethods(self):
        self.button_methods = {}
        self.button_args = {}
        self.button_kwargs = {}

    def callButtonMethod(self, key, *args, **kwargs):
        if key in self.button_methods:
            try: combined_args = args + self.button_args[key]
            except KeyError: combined_args = args
            try:
                combined_kwargs = copy.deepcopy(self.button_kwargs[key])
                combined_kwargs.update(kwargs)
            except KeyError: combined_kwargs = kwargs
            self.button_methods[key](*combined_args, **combined_kwargs)
        else:
            debugMessage("Undefined method for menu key: " + str(key))

    def setLayoutDimensions(self, *args, **kwargs):
        olddim = self.getLayoutDimensions()[:]
        super(MenuWidgetHelper, self).setLayoutDimensions(*args, **kwargs)
        if olddim != self.getLayoutDimensions():
            self._updateDimensions()

    def positionWidgets(self, *args, **kwargs):
        self._updateDimensions()
        super(MenuWidgetHelper, self).positionWidgets(*args, **kwargs)

    def _updateDimensions(self):
        self._createLayoutButtons()
        if self.fixed_dimensions:
            maxx = 0
            maxy = 0
            for widget in list(self.widgets.values()):
                width, height = widget.getWidgetDimensions()
                if width > maxx:
                    maxx = width
                if height > maxy:
                    maxy = height
            self.setFixedDistance(maxx + self.button_spacer[0], maxy + self.button_spacer[1])
            self.setWidgetDimensions(self.layout_offset[0]*2 + (maxx + self.button_spacer[0])*(self.layout_dimensions[0]-1),
                                self.layout_offset[1]*2 + (maxy + self.button_spacer[1])*(self.layout_dimensions[1]-1))
        else:
            #self.setFixedDistance(None,None)
            self.owner.resetHelperDimensions()

    def _createLayoutButtons(self):
        for x in range(self.getLayoutDimensions()[0]):
            for y in range(self.getLayoutDimensions()[1]):
                if (x,y) not in self.widgets:
                    self.addWidget(self.button_type, (x,y))
                    try: self.getButton((x,y)).setFont(self._button_font)
                    except AttributeError: pass

    def getButton(self, *args, **kwargs):
        return self.getWidget(*args, **kwargs)

    def getAllButtons(self):
        return list(self.widgets.values())

    def destroy(self):
        super(MenuWidgetHelper, self).destroy()
        self.button_methods = {}
        self.button_args = {}
        self.button_kwargs = {}



class MenuWidget(InterfaceWidget):
    def __init__(self, owner, index, bg = None, button_type = LabelWidget, width = None, height = None, columns = None, rows = None, *args, **kwargs):
        super(MenuWidget, self).__init__(owner, index, *args, **kwargs)
        self.border_spacing = DEFAULT_MENU_LAYOUT_OFFSET[:]
        self.helper_index = self.addWidget(MenuWidgetHelper, button_type = button_type, border_spacing = self.border_spacing)
        self.cursor_index = self.addWidget(InterfaceWidget)
        self.layout_center = (False, False)
        if bg is not None:
            self.setSprite(bg)
        self.allow_looping = True
        self.cursor_pos = (0,0)
        self.setCursorSprite()
        self.setCursorShow(False)
        self.setCursorLayer(DEFAULT_CURSOR_LAYER)
        self.setLayoutDisabled(True)
        self.setLayoutDimensions(columns, rows)
        self.setWidgetDimensions(width, height)


    def disableCursor(self): #is permanent
        self.removeWidget(self.cursor_index)
        self.cursor_index = None

    def setBorderSpacing(self, x = None, y = None):
        if x is None: x = self.border_spacing[0]
        if y is None: y = self.border_spacing[1]
        self.border_spacing = (x,y)
        try:
            self.widgets[self.helper_index].setLayoutOffset(*self.border_spacing)
        except KeyError:
            pass

    def getBorderSpacing(self):
        return self.border_spacing

    def setCursorPos(self, x = None, y = None):
        if x is None: x = self.cursor_pos[0]
        if y is None: y = self.cursor_pos[1]
        self.cursor_pos = (x,y)
        self.updateLayoutWindow()
        self.alignCursor()

    def getCursorPos(self):
        return self.cursor_pos

    def setCursorSprite(self, filename = None):
        if filename is None:
            filename = toStringPath(FULL_MISC_PATH + [DEFAULT_CURSOR_GRAPHIC]) #will not use the cursor's gpath and will use this explicit full path
        cursor = self.widgets[self.cursor_index]
        cursor.setSprite(filename)
        cursor.setSpriteOffset(-cursor.getSpriteWidth(), -cursor.getSpriteHeight()/2)

    def setCursorPath(self, *args, **kwargs):
        """won't update the sprite; call setCursorSprite again"""
        self.widgets[self.cursor_index].setSpritePath(*args, **kwargs)

    def setCursorShow(self, val):
        try:
            if val:
                self.widgets[self.cursor_index].unhideWidgets()
            else:
                self.widgets[self.cursor_index].hideWidgets()
        except KeyError:
            pass

    def alignCursor(self, index = None):
        if self.cursor_index is not None:
            if index is None:
                index = self.cursor_pos
            try: button = self.getButton(index)
            except KeyError: return #throw up our hands
            newpos = button.getSpriteLeftSide()
            self.widgets[self.cursor_index].setPositionOffset(*list(map(operator.sub, newpos , self.getPos())))
            self.widgets[self.cursor_index].setPos(*newpos)

    def setCursorLayer(self, *args, **kwargs):
        try:
            self.widgets[self.cursor_index].setGraphicalLayer(*args, **kwargs)
        except KeyError:
            pass

    def setCursorLayerExplicit(self, *args, **kwargs):
        try:
            self.widgets[self.cursor_index].setGraphicalLayerExplicit(*args, **kwargs)
        except KeyError:
            pass

    def setAllowLooping(self, val):
        self.allow_looping = val

    def _moveCursor(self, xy, direction):
        if self.cursor_index is not None:
            newval = self.cursor_pos[xy] + direction
            if self.allow_looping or (newval >= 0 and newval < self.getLayoutDimensions()[xy]):
                if newval < 0:
                    newval = self.getLayoutDimensions()[xy] - 1
                elif newval >= self.getLayoutDimensions()[xy]:
                    newval = 0
                args = list(self.getCursorPos())
                args[xy] = newval
                self.setCursorPos(*args)
                return True #movement successful
        return False #movement failed

    def updateLayoutWindow(self, newval = None, xy = None):
        if self.checkLayoutWindowDefined():
            if xy is None:
                for i in range(2):
                    self._updateLayoutWindow(newval, i)
            else:
                self._updateLayoutWindow(newval, xy)

    def _updateLayoutWindow(self, newval = None, xy = 0):
        if newval is None:
            newval = self.getCursorPos()[xy]
        window_dims = (self.getLayoutWindowXRange(), self.getLayoutWindowYRange())
        if window_dims[xy][0] > newval or window_dims[xy][1] <= newval:
            new_window_dims = list(self.getLayoutWindow())
            if window_dims[xy][0] > newval:
                difference = newval - new_window_dims[xy*2]
            else:
                difference = newval - new_window_dims[xy*2 + 1] + 1
            new_window_dims[xy*2] += difference
            new_window_dims[xy*2 + 1] += difference
            self.setLayoutWindow(*new_window_dims)
            self.positionWidgets()

    def resetHelperDimensions(self):
        self.widgets[self.helper_index].setWidgetDimensions(*list(map(operator.sub, self.getWidgetDimensions(), list(map(operator.mul, (2,2), self.border_spacing)))))

    #overwritten stuff

    def _respond(self, *args, **kwargs): #don't bother if this wigit isn't active
        if self.active:
            return super(MenuWidget, self)._respond(*args, **kwargs)
        return False

    def respondKeyPress(self, symbol, modifiers):
        if keyMatches(MOVE_UP, symbol):
            self._moveCursor(1, -1)
            return True
        elif keyMatches(MOVE_DOWN, symbol):
            self._moveCursor(1, 1)
            return True
        elif keyMatches(MOVE_RIGHT, symbol):
            self._moveCursor(0, 1)
            return True
        elif keyMatches(MOVE_LEFT, symbol):
            self._moveCursor(0, -1)
            return True
        elif keyMatches(CONFIRM, symbol):
            self.callButtonMethod(tuple(self.getCursorPos()))
            return True
        return False


    def activateWidget(self):
        super(MenuWidget, self).activateWidget()
        self.setCursorShow(True)

    def unactivateWidget(self):
        super(MenuWidget, self).unactivateWidget()
        self.setCursorShow(False)

    def positionWidgets(self, *args, **kwargs):
        super(MenuWidget, self).positionWidgets(*args, **kwargs)
        self.alignCursor()

    #container stuff
    def setFixedDimensions(self, *args, **kwargs):
        self.widgets[self.helper_index].setFixedDimensions(*args, **kwargs)

    def getFixedDimensions(self):
        return self.widgets[self.helper_index].getFixedDimensions()

    def setFixedDistance(self, *args, **kwargs):
        self.widgets[self.helper_index].setFixedDistance(*args, **kwargs)

    def setWidgetDimensions(self, *args, **kwargs):
        super(MenuWidget, self).setWidgetDimensions(*args, **kwargs)
        self.resetHelperDimensions()
        self.setSpriteDimensions(*self.getWidgetDimensions())

    def setButtonSpacer(self, *args, **kwargs):
        self.widgets[self.helper_index].setButtonSpacer(*args, **kwargs)

    def setButtonType(self, *args, **kwargs): #will not update previously created buttons
        self.widgets[self.helper_index].setButtonType(*args, **kwargs)

    def replaceButton(self, *args, **kwargs):
        self.widgets[self.helper_index].replaceButton(*args, **kwargs)

    def setButtonMethod(self, *args, **kwargs):
        self.widgets[self.helper_index].setButtonMethod(*args, **kwargs)

    def setButtonText(self, *args, **kwargs):
        self.widgets[self.helper_index].setButtonText(*args, **kwargs)

    def setButtonFont(self, *args, **kwargs):
        self.widgets[self.helper_index].setButtonFont(*args, **kwargs)

    def setButtonColor(self, *args, **kwargs):
        self.widgets[self.helper_index].setButtonColor(*args, **kwargs)

    def callButtonMethod(self, *args, **kwargs):
        self.widgets[self.helper_index].callButtonMethod(*args, **kwargs)

    def setLayoutDimensions(self, *args, **kwargs): #overwrites regular version
        self.widgets[self.helper_index].setLayoutDimensions(*args, **kwargs)

    def getLayoutDimensions(self):
        return self.widgets[self.helper_index].getLayoutDimensions()

    def setLayoutFlush(self, *args, **kwargs):
        self.widgets[self.helper_index].setLayoutFlush(*args, **kwargs)

    def setLayoutWindow(self, *args, **kwargs):
        self.widgets[self.helper_index].setLayoutWindow(*args, **kwargs)

    def setLayoutCenter(self, *args, **kwargs):
        self.widgets[self.helper_index].setLayoutCenter(*args, **kwargs)

    def getLayoutWindow(self):
        return self.widgets[self.helper_index].getLayoutWindow()

    def getLayoutWindowXRange(self):
        return self.widgets[self.helper_index].getLayoutWindowXRange()

    def getLayoutWindowYRange(self):
        return self.widgets[self.helper_index].getLayoutWindowYRange()

    def checkLayoutWindowDefined(self):
        try: return self.widgets[self.helper_index].checkLayoutWindowDefined()
        except (AttributeError, KeyError): return False

    def getButton(self, *args, **kwargs): #just a mirror of getWidget for the helper's buttons
        return self.widgets[self.helper_index].getButton(*args, **kwargs)

    def getAllButtons(self):
        return self.widgets[self.helper_index].getAllButtons()

