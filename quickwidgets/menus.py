# -*- coding: utf-8 -*-

import operator, math

from kaiengine.gconfig import FULL_MISC_PATH, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_FLIP_LOOKUP

from kaiengine.display import getWindowDimensionsScaled
from kaiengine.interface import ScreenElement
from kaiengine.event import callQuery
from kaiengine.utilityFuncs import dictUnion

from .containers import VerticalContainer, HorizontalContainer, GridContainer
from .buttons import LabelButton
from .stylesheetkeys import DEFAULT_GRAPHIC, DEFAULT_BORDER, DEFAULT_MENU_GRAPHIC, DEFAULT_MENU_BORDER, DEFAULT_MENU_WIDTH, DEFAULT_MENU_HEIGHT

MOVE_OFFSETS = {DIRECTION_UP: (0,1),
                DIRECTION_DOWN: (0,-1),
                DIRECTION_RIGHT: (1,0),
                DIRECTION_LEFT: (-1,0)}

INTERLINK_EVENT_LEFT = "interlinkleft"
INTERLINK_EVENT_RIGHT = "interlinkright"
INTERLINK_EVENT_UP = "interlinkup"
INTERLINK_EVENT_DOWN = "interlinkdown"

MENU_LOOKUP_KEY = "MENU_LOOKUP"

class MenuTemplate(ScreenElement):
    #not to be used without a container

    #update event list
    other_event_keys = ScreenElement.other_event_keys + (INTERLINK_EVENT_LEFT, INTERLINK_EVENT_RIGHT, INTERLINK_EVENT_UP, INTERLINK_EVENT_DOWN)

    button_type = LabelButton
    focus_first_button = True

    stylesheet = dictUnion(ScreenElement.stylesheet, {})

    def __init__(self, sprite_path = None, button_type = None, **kwargs):
        super().__init__(**kwargs)
        sprite_path = sprite_path or self.getOrderedStylesheetData(DEFAULT_MENU_GRAPHIC, DEFAULT_GRAPHIC, default=tuple(FULL_MISC_PATH + ["menugraphics", "menu0.bordered"]))
        if sprite_path:
            self.setSprite(sprite_path)
        if button_type is not None:
            self.button_type = button_type
        self._first_button = True
        self._buttons = set()
        self._menu_interlinks = {}

        #overwrites
        self.border = self.stylesheet.get(DEFAULT_BORDER, None) or self.stylesheet.get(DEFAULT_MENU_BORDER, None) or (8,8)

        #defaults
        self.setSpriteCenter(True, True)
        self.setSpriteFollowCamera(True)
        self.setPos(*map(operator.truediv, getWindowDimensionsScaled(), (2,2)))

        self.addQueryListener(self.getEventID(MENU_LOOKUP_KEY), lambda: self)

    def setButtonType(self, newtype):
        #will NOT regenerate old buttons!
        self.button_type = newtype

    def addButton(self, *args, **kwargs):
        ID = self.addChildApplyStylesheet(self.button_type, *args, **kwargs)
        self._updateFirstButton(ID)
        self._buttons.add(ID)
        return ID

    def getButton(self, *args, **kwargs):
        #alias for getChildByKey
        return self.getChildByKey(*args, **kwargs)

    def getAllButtons(self):
        return [self.getChild(ID) for ID in self._buttons]

    def _updateFirstButton(self, ID):
        if self._first_button:
            if self.focus_first_button:
                self.setFocus(ID)
            self._first_button = False

    def interlinkMenu(self, direction, othermenuid):
        othermenu = self.queryMenuByID(othermenuid)
        if othermenu:
            self._interlinkMenu(direction, othermenu.id)
            othermenu._interlinkMenu(DIRECTION_FLIP_LOOKUP[direction], self.id)

    def _interlinkMenu(self, direction, othermenuid):
        try:
            self._menu_interlinks[direction].add(othermenuid)
        except KeyError:
            self._menu_interlinks[direction] = set()
            self._menu_interlinks[direction].add(othermenuid)

    def clearInterlink(self, direction, othermenuid):
        othermenu = self.queryMenuByID(othermenuid)
        if othermenu:
            self._clearInterlink(direction, othermenu.id)
            othermenu._clearInterlink(DIRECTION_FLIP_LOOKUP[direction], self.id)

    def _clearInterlink(self, direction, othermenuid):
        try:
            self._menu_interlinks[direction].discard(othermenuid)
        except KeyError:
            pass

    def clearAllInterlinks(self):
        for direction, menuref in self.getAllInterlinkedMenus():
            menuref._clearInterlink(DIRECTION_FLIP_LOOKUP[direction], self.id)
        self._menu_interlinks.clear()


    def _interlinkActivate(self, direction):
        if direction in self._menu_interlinks:
            pos = self.getFocusedChild().getCenterPosition()
            mindistance = math.inf
            mindistance_menu_ref = None
            mindistance_button_id = None
            for menu_id in self._menu_interlinks[direction]:
                menu_ref = self.queryMenuByID(menu_id)
                if menu_ref:
                    for button in menu_ref.getAllButtons():
                        other_pos = button.getCenterPosition()
                        distance = math.hypot(pos[0] - other_pos[0], pos[1] - other_pos[1])
                        if distance < mindistance:
                            mindistance = distance
                            mindistance_menu_ref = menu_ref
                            mindistance_button_id = button.id
            if mindistance_menu_ref: #TODO: make this suck less
                self.clearFocus()
                self.getParent().clearFocus()
                mindistance_menu_ref.setFocus(mindistance_button_id)
                mindistance_menu_ref.setSelfFullyFocused()
                return True
        return False

    def getAllInterlinkedMenus(self):
        menulist = []
        for direction, menuset in self._menu_interlinks.items():
            for menuid in menuset:
                menuref = self.queryMenuByID(menuid)
                if menuref:
                    menulist.append((direction, menuref))
        return menulist

    def queryMenuByID(self, menu_id):
        try:
            menu_id.id
        except AttributeError:
            return callQuery(self._getEventID(menu_id, MENU_LOOKUP_KEY))
        else:
            return menu_id #is a reference

    #input stuff

    def mouseover(self, *args, **kwargs):
        if not self.isInputLocked():
            self.setSelfFullyFocused()

    #overwritten stuff

    def setFocus(self, *args, **kwargs):
        super().setFocus(*args, **kwargs)
        if self.hasFocusedChild():
            for direction, menuref in self.getAllInterlinkedMenus():
                menuref.clearFocus()


    def removeChild(self, *args, **kwargs):
        ID = super().removeChild(*args, **kwargs)
        self._buttons.discard(ID)
        return ID

    def removeAllChildren(self, *args, **kwargs):
        super().removeAllChildren(*args, **kwargs)
        self._buttons.clear()

    def setSpriteCenter(self, *args, **kwargs):
        super().setSpriteCenter(*args, **kwargs)
        self._applyChildrenPositions()

    def _updateContainerPositions(self, *args, **kwargs):
        maxwidth = 0
        maxheight = 0
        for button in self.getAllButtons():
            try:
                button.updateContainerPositions
            except:
                pass
            else:
                button.updateContainerPositions()
            maxwidth = max(maxwidth, button.getWidth())
            maxheight = max(maxheight, button.getHeight())
        for button in self.getAllButtons():
            button.setDimensions(maxwidth, maxheight)
        super()._updateContainerPositions(*args, **kwargs)


class VerticalMenu(MenuTemplate, VerticalContainer):

    #input stuff

    def moveleft(self):
        returnval = self.callEventFunc(INTERLINK_EVENT_LEFT)
        return self._interlinkActivate(DIRECTION_LEFT) or returnval

    def moveright(self):
        returnval = self.callEventFunc(INTERLINK_EVENT_RIGHT)
        return self._interlinkActivate(DIRECTION_RIGHT) or returnval

    def moveup(self):
        if self.hasFocusedChild():
            key = self.getChildKey(self.getFocusedChild())
            if key == 0:
                self.callEventFunc(INTERLINK_EVENT_UP)
                if self._interlinkActivate(DIRECTION_UP):
                    return True
            self.setFocus(self.getChildByKey((key - 1) % self.getLength()))
            return True

    def movedown(self):
        if self.hasFocusedChild():
            key = self.getChildKey(self.getFocusedChild())
            if key >= self.getLength() - 1:
                self.callEventFunc(INTERLINK_EVENT_DOWN)
                if self._interlinkActivate(DIRECTION_DOWN):
                    return True
            self.setFocus(self.getChildByKey((self.getChildKey(self.getFocusedChild()) + 1) % self.getLength()))
            return True


class HorizontalMenu(MenuTemplate, HorizontalContainer):

    #input stuff

    def moveup(self):
        returnval = self.callEventFunc(INTERLINK_EVENT_UP)
        return self._interlinkActivate(DIRECTION_UP) or returnval

    def movedown(self):
        returnval = self.callEventFunc(INTERLINK_EVENT_DOWN)
        return self._interlinkActivate(DIRECTION_DOWN) or returnval

    def moveleft(self):
        if self.hasFocusedChild():
            key = self.getChildKey(self.getFocusedChild())
            if key == 0:
                self.callEventFunc(INTERLINK_EVENT_LEFT)
                if self._interlinkActivate(DIRECTION_LEFT):
                    return True
            self.setFocus(self.getChildByKey((key - 1) % self.getLength()))
            return True

    def moveright(self):
        if self.hasFocusedChild():
            key = self.getChildKey(self.getFocusedChild())
            if key >= self.getLength() - 1:
                self.callEventFunc(INTERLINK_EVENT_RIGHT)
                if self._interlinkActivate(DIRECTION_RIGHT):
                    return True
            self.setFocus(self.getChildByKey((key + 1) % self.getLength()))
            return True


class GridMenu(MenuTemplate, GridContainer):

    def _move(self, direction):
        xstep, ystep = MOVE_OFFSETS[direction]
        grid_sizes = self.getGridSizes()
        x, y = self.getChildKey(self.getFocusedChild())
        x += xstep
        y += ystep
        interlink_event = False
        while not (x, y) in self._child_pos_dict:
            x += xstep
            y += ystep
            if x < grid_sizes[0]:
                self.callEventFunc(INTERLINK_EVENT_LEFT)
                if self._interlinkActivate(DIRECTION_LEFT):
                    interlink_event = True
                    break
                x = grid_sizes[1]
            elif x > grid_sizes[1]:
                self.callEventFunc(INTERLINK_EVENT_RIGHT)
                if self._interlinkActivate(DIRECTION_RIGHT):
                    interlink_event = True
                    break
                x = grid_sizes[0]
            if y < grid_sizes[2]:
                self.callEventFunc(INTERLINK_EVENT_DOWN)
                if self._interlinkActivate(DIRECTION_DOWN):
                    interlink_event = True
                    break
                y = grid_sizes[3]
            elif y > grid_sizes[3]:
                self.callEventFunc(INTERLINK_EVENT_UP)
                if self._interlinkActivate(DIRECTION_UP):
                    interlink_event = True
                    break
                y = grid_sizes[2]
        if not interlink_event:
            self.setFocus(self.getChildByKey((x, y)))

    #input stuff

    def moveleft(self):
        if self.hasFocusedChild():
            self._move(DIRECTION_LEFT)
            return True

    def moveright(self):
        if self.hasFocusedChild():
            self._move(DIRECTION_RIGHT)
            return True

    def moveup(self):
        if self.hasFocusedChild():
            self._move(DIRECTION_UP)
            return True

    def movedown(self):
        if self.hasFocusedChild():
            self._move(DIRECTION_DOWN)
            return True


    #overwritten stuff
    def addButton(self, pos_tuple, *args, **kwargs):
        ID = self.addChildApplyStylesheet(pos_tuple, self.button_type, *args, **kwargs)
        self._updateFirstButton(ID)
        self._buttons.add(ID)
        return ID
