

import operator, weakref
from kaiengine.objectinterface import GraphicInterface, EventInterface
from kaiengine.display import getWindowDimensionsScaled
from kaiengine.uidgen import generateUniqueID

from kaiengine.gconfig import *

WINDOW_KEY = "window_hide"


class InterfaceWidget(GraphicInterface, EventInterface):
    def __init__(self, owner, index, *args, **kwargs):
        self._uid = generateUniqueID("interface_widget")
        self._owner = None
        self._widget_layer = 0
        self.owner = owner
        self.index = index
        self.graphical_layer = None
        super(InterfaceWidget, self).__init__(*args, **kwargs)
        self.widget_dimensions = (0,0)
        self.layout_dimensions = (1,1)
        self.layout_flush = False
        self.layout_flow = LAYOUT_FLOW_HORIZONTAL
        self.layout_center = (True, True)
        self.layout_offset = (0,0) #applied to all child widgets
        self.layout_fixed_distance = (None,None) #fixed distance between widgets in layout
        self.layout_stretch = (False, False)
        self.layout_window = (None, None, None, None)
        self.layout_disabled = False
        self.position_offset = (0,0) #just itself
        self.active_widget = None
        self.active = False #set to true if set as parent's active widget (all widgets set to false if no active widget)
        self.widget_hidden = False
        self.widget_hidden_ids = set()
        self._old_sprite_show = None
        self.widgets = {}


    @property
    def owner(self):
        try:
            return self._owner()
        except:
            return None

    @owner.setter
    def owner(self, val):
        try:
            val() #check if weakref
            self._owner = val
        except:
            try:
                self._owner = weakref.ref(val)
            except:
                self._owner = None

    @property
    def width(self):
        return self.getWidth()

    @property
    def height(self):
        return self.getHeight()

    def getWidgetPos(self):
        """get relative position within the widget. Not valid until after positionWidgets used"""
        try:
            owner_pos = self.owner.getPos()
        except:
            owner_pos = [0,0]
        return list(map(operator.sub, self.getPos(), owner_pos))


    def getWidgetID(self):
        return self._uid

    #overwritten stuff


    def setSpriteDefaults(self, *args, **kwargs): #from graphic interface
        super(InterfaceWidget, self).setSpriteDefaults(*args, **kwargs)
        self._follow_camera = True
        self._layer = self.getGraphicalLayerExplicit()

    #widget creation

    def addWidget(self, widget_type, index = None, *args, **kwargs):
        if index is None:
            index = self.findFreeIndex()
        self.widgets[index] = widget_type(self, index, *args, **kwargs)
        if self.checkLayoutWindowDefined() and (index[0] not in list(range(*self.getLayoutWindowXRange())) or index[1] not in list(range(*self.getLayoutWindowYRange()))):
            self.widgets[index].hideWidgets(self.getWidgetID() + WINDOW_KEY)
        for identifier in self.widget_hidden_ids:
            self.widgets[index].hideWidgets(identifier)
        return index


    def removeWidget(self, key):
        try:
            if self.active_widget == key:
                self.unsetActiveWidget()
            self.widgets[key].destroy()
            del self.widgets[key]
        except KeyError:
            pass

    def removeAllWidgets(self):
        for key in list(self.widgets.keys()):
            self.removeWidget(key)

    def findFreeIndex(self, direction = None):
        x = 0
        y = 0
        if direction is None:
            direction = self.layout_flow
        if direction == LAYOUT_FLOW_HORIZONTAL:
            while (x,y) in self.widgets:
                x += 1
                if x >= self.layout_dimensions[0]:
                    x = 0
                    y += 1
        else:
            while (x,y) in self.widgets:
                y += 1
                if y >= self.layout_dimensions[1]:
                    y = 0
                    x += 1
        return (x,y)

    def getWidget(self, key):
        return self.widgets[key]

    #layout stuff

    def setLayoutDisabled(self, val):
        self.layout_disabled = val

    def setLayoutDimensions(self, x = None, y = None, purge = True):
        if x is None: x = self.layout_dimensions[0]
        if y is None: y = self.layout_dimensions[1]
        self.layout_dimensions = (max(x,1),max(y,1))
        if purge:
            self.purgeWidgets()

    def getLayoutDimensions(self):
        return self.layout_dimensions

    def setLayoutOffset(self, x = None, y = None):
        if x is None: x = self.layout_offset[0]
        if y is None: y = self.layout_offset[1]
        self.layout_offset = (x,y)

    def getLayoutOffset(self):
        return self.layout_offset

    def setLayoutStretch(self, x = None, y = None):
        if x is None: x = self.layout_stretch[0]
        if y is None: y = self.layout_stretch[1]
        self.layout_stretch = (x,y)

    def setLayoutCenter(self, x = None, y = None):
        if x is None: x = self.layout_center[0]
        if y is None: y = self.layout_center[1]
        self.layout_center = (x,y)

    def setPositionOffset(self, x = None, y = None):
        if x is None: x = self.position_offset[0]
        if y is None: y = self.position_offset[1]
        self.position_offset = (x,y)

    def getPositionOffset(self):
        return self.position_offset

    def setFixedDistance(self, x = "_none", y = "_none"):
        if x == "_none": x = self.layout_fixed_distance[0]
        if y == "_none": y = self.layout_fixed_distance[1]
        self.layout_fixed_distance = (x,y)

    def setLayoutFlush(self, val):
        self.layout_flush = val

    def setLayoutWindow(self, xlow = "_none", xhigh = "_none", ylow = "_none", yhigh = "_none", hide = True):
        if xlow is "_none": xlow = self.layout_window[0]
        if xhigh is "_none": xhigh = self.layout_window[1]
        if ylow is "_none": ylow = self.layout_window[2]
        if yhigh is "_none": yhigh = self.layout_window[3]
        self.layout_window = (xlow, xhigh, ylow, yhigh)
        if hide:
            x_range = self.getLayoutWindowXRange()
            y_range = self.getLayoutWindowYRange()
            for x in range(x_range[0]):
                for y in range(self.layout_dimensions[1]):
                    try: self.widgets[(x,y)].hideWidgets(self.getWidgetID() + WINDOW_KEY)
                    except KeyError: pass
            for x in range(x_range[1], self.layout_dimensions[0]):
                for y in range(self.layout_dimensions[1]):
                    try: self.widgets[(x,y)].hideWidgets(self.getWidgetID() + WINDOW_KEY)
                    except KeyError: pass
            for x in range(*x_range):
                for y in range(y_range[0]):
                    try: self.widgets[(x,y)].hideWidgets(self.getWidgetID() + WINDOW_KEY)
                    except KeyError: pass
                for y in range(*y_range):
                    try: self.widgets[(x,y)].unhideWidgets(self.getWidgetID() + WINDOW_KEY)
                    except KeyError: pass
                for y in range(y_range[1], self.layout_dimensions[1]):
                    try: self.widgets[(x,y)].hideWidgets(self.getWidgetID() + WINDOW_KEY)
                    except KeyError: pass

    def getLayoutWindow(self):
        return self.layout_window

    def getLayoutWindowXRange(self):
        return self._getLayoutWindowXRange()

    def _getLayoutWindowXRange(self):
        return ((0 if self.layout_window[0] is None else self.layout_window[0]),
                (self.layout_dimensions[0] if self.layout_window[1] is None else self.layout_window[1]))

    def getLayoutWindowYRange(self):
        return self._getLayoutWindowYRange()

    def _getLayoutWindowYRange(self):
        return ((0 if self.layout_window[2] is None else self.layout_window[2]),
                (self.layout_dimensions[1] if self.layout_window[3] is None else self.layout_window[3]))

    def getLayoutWindowRanges(self):
        return self._getLayoutWindowRanges()

    def _getLayoutWindowRanges(self):
        return self.getLayoutWindowXRange() + self.getLayoutWindowYRange()

    def getLayoutWindowDimensions(self):
        x_range = self.getLayoutWindowXRange()
        y_range = self.getLayoutWindowYRange()
        return x_range[1] - x_range[0], y_range[1] - y_range[0]

    def checkLayoutWindowDefined(self):
        return self.layout_window != (None,None,None,None)

    def purgeWidgets(self):
        for key in list(self.widgets.keys()):
            try:
                if key[0] >= self.layout_dimensions[0] or key[1] >= self.layout_dimensions[1]:
                    raise TypeError #hack to avoid duplicate code
            except TypeError: #check for weird non-tuple keys
                try:
                    self.widgets[key].destroy()
                except:
                    pass
                del self.widgets[key]

    def positionWidgets(self, recursive = True):
        if self.owner is not None:
            owner_pos = self.getBottomLeftCorner()
        else:
            owner_pos = [0,0]
        if not self.layout_disabled:
            x_range = self._getLayoutWindowXRange()
            y_range = self._getLayoutWindowYRange()
            x_size = x_range[1] - x_range[0]
            y_size =  y_range[1] - y_range[0]
            if self.layout_fixed_distance[0] is not None:
                xpos = self.layout_fixed_distance[0]
            else:
                xpos = self.width / x_size
            if self.layout_fixed_distance[1] is not None:
                ypos = self.layout_fixed_distance[1]
            else:
                ypos = self.height / y_size
            position_offset = [xpos, ypos]
            center_offset = [0,0]
            if self.layout_center[0]:
                center_offset[0] = position_offset[0] / 2
            if self.layout_center[1]:
                center_offset[1] = position_offset[1] / 2
            xcounter = 0
            for x in range(*x_range):
                ycounter = 0
                for y in range(*y_range):
                    key = (x,y)
                    try:
                        widget = self.widgets[key]
                    except KeyError:
                        pass
                    else:
                        position = (xcounter, -(ycounter + 1 - y_size))
                        widget.setSpriteCenter(*self.layout_center)
                        widget.updateSpriteLayer()
                        widget.setPos(*list(map(operator.add, widget.getPositionOffset(), list(map(operator.add, owner_pos, list(map(operator.add, self.layout_offset, list(map(operator.add, center_offset, list(map(operator.mul, position, position_offset)))))))))))
                    ycounter += 1
                xcounter += 1
            if self.layout_flow == LAYOUT_FLOW_HORIZONTAL:
                for y in range(*y_range):
                    for x in range(*x_range):
                        try:
                            xoffset = -1
                            if self.layout_flush:
                                xoffset = self._getHighestX(x,y)
                                if xoffset != 0:
                                    self.widgets[(x,y)].setPos(x = xoffset)
                                self.widgets[(x,y)].setSpriteCenter(x = False)
                            if self.widgets[(x,y)].layout_stretch[0]:
                                if xoffset == -1: #efficiency thing; I could probably restructure instead but laaaazy
                                    xoffset = self._getHighestX(x,y)
                                self.widgets[(x,y)].width = getWindowDimensionsScaled()[0] - xoffset
                                self.widgets[(x,y)].setPos(x = xoffset + owner_pos[0])
                                self.widgets[(x,y)].setSpriteCenter(x = False)
                            if self.widgets[(x,y)].layout_stretch[1]:
                                self.widgets[(x,y)].height = getWindowDimensionsScaled()[1] - self._getHighestY(x,y)
                                self.widgets[(x,y)].setPos(y = owner_pos[1])
                                self.widgets[(x,y)].setSpriteCenter(y = False)
                        except KeyError:
                            pass
            else:
                for x in range(*x_range):
                    for y in range(*y_range):
                        try:
                            yoffset = -1
                            if self.widgets[(x,y)].layout_stretch[1]:
                                yoffset = self._getHighestY(x,y)
                                self.widgets[(x,y)].height = getWindowDimensionsScaled()[0] - yoffset
                                self.widgets[(x,y)].setPos(y = owner_pos[1])
                                self.widgets[(x,y)].setSpriteCenter(y = False)
                            if self.widgets[(x,y)].layout_stretch[0]:
                                xoffset = self._getHighestX(x,y)
                                self.widgets[(x,y)].width = getWindowDimensionsScaled()[0] - xoffset
                                self.widgets[(x,y)].setPos(x = xoffset + owner_pos[0])
                                self.widgets[(x,y)].setSpriteCenter(x = False)
                            if self.layout_flush:
                                if yoffset == -1:
                                    yoffset = self._getHighestY(x,y)
                                self.widgets[(x,y)].setPos(y = yoffset - self.widgets[(x,y)].height + owner_pos[1])
                                self.widgets[(x,y)].setSpriteCenter(y = False)
                        except KeyError:
                            pass
        else:
            for widget in list(self.widgets.values()):
                widget.setPos(*list(map(operator.add, widget.getPositionOffset(), list(map(operator.add, owner_pos, self.layout_offset)))))
                widget.updateSpriteLayer()
        if recursive:
            for widget in list(self.widgets.values()):
                widget.positionWidgets(recursive)


    def _getHighestX(self, column, row):
        highest = 0
        if self.layout_flow == LAYOUT_FLOW_HORIZONTAL:
            for y in range(self.getLayoutWindowYRange()[0], row + 1):
                for x in range(self.getLayoutWindowXRange()[0], column):
                    highest = self.__getHighestX(x, y, column, row, highest)
        else:
            for y in range(*self.getLayoutWindowYRange()):
                for x in range(self.getLayoutWindowXRange()[0], column):
                    highest = self.__getHighestX(x, y, column, row, highest)
        return highest

    def __getHighestX(self, x, y, column, row, highest):
        try:
            if self.widgets[(x,y)].getSpriteTopSide()[1] >= self.widgets[(column,row)].getSpriteBottomSide()[1] and self.widgets[(x,y)].getSpriteBottomSide()[1] <= self.widgets[(column,row)].getSpriteTopSide()[1]:
                newx = self.widgets[(x,y)].getSpriteRightSide()[0]
                if newx > highest:
                    return newx
        except KeyError:
            pass
        return highest

    def _getHighestY(self, column, row):
        highest = 0
        if self.layout_flow == LAYOUT_FLOW_HORIZONTAL:
            for y in range(self.getLayoutWindowYRange()[0],row):
                for x in range(*self.getLayoutWindowXRange()):
                    highest = self.__getHighestY(x, y, column, row, highest)
        else:
            for y in range(self.getLayoutWindowYRange()[0],row):
                for x in range(self.getLayoutWindowXRange()[0], column + 1):
                    highest = self.__getHighestY(x, y, column, row, highest)
        return highest

    def __getHighestY(self, x, y, column, row, highest):
        try:
            if self.widgets[(x,y)].getSpriteRightSide()[0] >= self.widgets[(column,row)].getSpriteLeftSide()[0] and self.widgets[(x,y)].getSpriteLeftSide()[0] <= self.widgets[(column,row)].getSpriteRightSide()[0]:
                newy = self.widgets[(x,y)].getSpriteBottomSide()[1]
                if newy > highest:
                    return newy
        except KeyError:
            pass
        return highest

    def setWidgetDimensions(self, x = None, y = None):
        if x is None: x = self.width
        if y is None: y = self.height
        x = max(x, 0)
        y = max(y, 0)
        self.widget_dimensions = (x,y)

    def getWidgetDimensions(self):
        return self.widget_dimensions
    
    def getWidth(self):
        return self.widget_dimensions[0]
    
    def getHeight(self):
        return self.widget_dimensions[1]

    def setGraphicalLayer(self, amount):
        self._widget_layer = amount

    def getGraphicalLayer(self):
        return self._widget_layer

    def setGraphicalLayerExplicit(self, newlayer, offset = True):
        if offset:
            self.graphical_layer = None #necessary for getGraphicalLayer
            added_offset = self.getGraphicalLayerExplicit()
        else:
            added_offset = 0
        self.graphical_layer = newlayer + added_offset

    def getGraphicalLayerExplicit(self):
        if self.graphical_layer is None:
            try:
                return float(self.owner.getGraphicalLayerExplicit()) + self._getLayerIncrement()*(self.getGraphicalLayer()+1)
            except AttributeError:
                return 0
        return self.graphical_layer

    def _getLayerIncrement(self):
        return WIDGET_GRAPHICAL_INCREMENT

    def updateSpriteLayer(self):
        self.setSpriteLayer(self.getGraphicalLayerExplicit())

    def setActiveWidget(self, index):
        self.unsetActiveWidget()
        self.active_widget = index
        self.widgets[self.active_widget].activateWidget()

    def getActiveWidget(self):
        return self.active_widget

    def unsetActiveWidget(self):
        try:
            self.widgets[self.active_widget].unactivateWidget()
        except KeyError:
            pass
        self.active_widget = None

    def activateWidget(self): #overwritable
        self.active = True

    def unactivateWidget(self): #overwritable
        self.active = False

    def hideWidgets(self, widget_id = None):
        if widget_id is None:
            widget_id = self.getWidgetID()
        for widget in self.widgets.values():
            widget.hideWidgets(widget_id)
        returnval = widget_id not in self.widget_hidden_ids
        self.widget_hidden_ids.add(widget_id)
        if not self.widget_hidden:
            self.widget_hidden = True
            self._old_sprite_show = self.getSpriteShow()
            self.setSpriteShow(False)
        return returnval #returns whether this operation was successful or not (true if widget_id was not previously hidden)

    def unhideWidgets(self, widget_id = None):
        if widget_id is None:
            widget_id = self.getWidgetID()
        for widget in list(self.widgets.values()):
            widget.unhideWidgets(widget_id)
        try:
            self.widget_hidden_ids.remove(widget_id)
            returnval = True
        except KeyError:
            returnval = False
        if self.widget_hidden and len(self.widget_hidden_ids) <= 0:
            self.widget_hidden = False
            if self._old_sprite_show is not None:
                self.setSpriteShow(self._old_sprite_show)
                self._old_sprite_show = None
        return returnval #returns whether this operation was successful or not (true if the widget_id was previously hidden)
    
    def setAllWidgetsAlpha(self, alpha):
        for widget in self.widgets.values():
            widget.setAllWidgetsAlpha(alpha)
        self.setSpriteAlpha(alpha)

    #overwritable functions

    def respondKeyPress(self, symbol):
        """Respond to a key being pressed."""
        return False

    def respondKeyRelease(self, symbol):
        """Respond to a key being released."""
        return False

    def respondMousePress(self, x, y, button):
        """Respond to a mouse button being pressed."""
        return False

    def respondMouseRelease(self, x, y, button):
        """Respond to a mouse button being released."""
        return False

    def respondMouseMove(self, x, y, dx, dy):
        """Respond to the mouse cursor moving."""
        return False

    def respondMouseDrag(self, x, y, dx, dy, button):
        """Respond to the mouse cursor moving with a button held down."""
        return False

    def respondMouseEnter(self, x, y):
        """Respond to the mouse cursor entering the window."""
        return False

    def respondMouseExit(self, x, y):
        """Respond to the mouse cursor leaving the window."""
        return False

    def respondJoybuttonPress(self, joystick, button):
        """Respond to a controller button being pressed."""
        return False


    #response logic

    def _respond(self, method1, method2name, *args, **kwargs):
        if not self.widget_hidden:
            if self.active_widget is None or self.active_widget not in self.widgets:
                for widget in list(self.widgets.values()):
                    if getattr(widget, method2name)(*args, **kwargs):
                        return True
                return method1(*args, **kwargs)
            else:
                if getattr(self.widgets[self.active_widget], method2name)(*args, **kwargs):
                    return True
                return method1(*args, **kwargs)
        return False

    def _respondKeyPress(self, *args, **kwargs):
        return self._respond(self.respondKeyPress, "_respondKeyPress", *args, **kwargs)

    def _respondKeyRelease(self, *args, **kwargs):
        return self._respond(self.respondKeyRelease, "_respondKeyRelease", *args, **kwargs)

    def _respondMousePress(self, *args, **kwargs):
        return self._respond(self.respondMousePress, "_respondMousePress", *args, **kwargs)

    def _respondMouseRelease(self, *args, **kwargs):
        return self._respond(self.respondMouseRelease, "_respondMouseRelease", *args, **kwargs)

    def _respondMouseMove(self, *args, **kwargs):
        return self._respond(self.respondMouseMove, "_respondMouseMove", *args, **kwargs)

    def _respondMouseDrag(self, *args, **kwargs):
        return self._respond(self.respondMouseDrag, "_respondMouseDrag", *args, **kwargs)

    def _respondMouseEnter(self, *args, **kwargs):
        return self._respond(self.respondMouseEnter, "_respondMouseEnter", *args, **kwargs)

    def _respondMouseExit(self, *args, **kwargs):
        return self._respond(self.respondMouseExit, "_respondMouseExit", *args, **kwargs)

    def _respondJoybuttonPress(self, *args, **kwargs):
        return self._respond(self.respondJoybuttonPress, "_respondJoybuttonPress", *args, **kwargs)




    def destroy(self):
        super(InterfaceWidget, self).destroy()
        for key in list(self.widgets.keys()):
            self.removeWidget(key)
        self.widgets = {}
        self.owner = None
