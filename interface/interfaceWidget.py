from kaiengine.gconfig import *
from kaiengine.interface.spriteHandler import makeSprite, registerSprite, removeSprite
from kaiengine.display import getWindowDimensionsScaled
from kaiengine.event import addCustomListener, removeCustomListener
from kaiengine.objectinterface import EventInterface
from kaiengine.objectdestroyederror import ObjectDestroyedError

class InterfaceWidget(EventInterface):

    """Base class for display of interface elements.

        init parameters:

        anchorPosition: base screen coordinates used for positioning widget
        followCamera: all widget elements will follow camera
        internalPositionOffset: alters positioning of this widget without affecting the rest of a layout it's in
        layout parameters:
            arrangement: 'vertical', 'horizontal', 'none', or 'grid' (NYI)
            horizontalAlignment: 'left' or 'right' (or NYI, 'centered')
            verticalAlignment: 'bottom' or 'top' (or NYI, 'centered')
            horizontalPadding: pixels of horizontal padding between subwidgets
            verticalPadding: pixels of vertical padding between subwidgets
            reverseArrangement: whether arrangement should be mirrored
            collapseColumns: (only for grids) whether columns should be collapsed
            collapseRows: (only for grids) whether rows should be collapsed
                (collapsed dimensions will be squished on a per-row/column basis
                instead of being aligned to the largest perpendicular cell's dimensions)
    """

    def __init__(self, anchorPosition = (0, 0), followCamera = False, internalPositionOffset = (0, 0), arrangement = "vertical", horizontalAlignment = "left", verticalAlignment = "bottom", horizontalPadding = 0, verticalPadding = 0, reverseArrangement = False, collapseColumns = False, collapseRows = False, explicitColumnSize = None, explicitRowSize = None, baseLayer=0, flipSprites=(False, False)):
        super(InterfaceWidget, self).__init__()
        self.sprites = []
        self._spriteOffsets = {}
        self.widgets = []
        self.hidden = False
        self._anchorPosition = anchorPosition
        self.layoutStyle = {"arrangement": arrangement,
                            "horizontalAlignment": horizontalAlignment,
                            "verticalAlignment": verticalAlignment,
                            "horizontalPadding": horizontalPadding,
                            "verticalPadding": verticalPadding,
                            "reverseArrangement": reverseArrangement,
                            "collapseRows": collapseColumns,
                            "collapseColumns": collapseRows,
                            "explicitColumnSize":explicitColumnSize,
                            "explicitRowSize":explicitRowSize}
        self._followCamera = followCamera
        self.internalPositionOffset = internalPositionOffset
        self._baseLayer = baseLayer
        self.flipSprites = flipSprites
        self.being_destroyed = False
        self._custom_listeners = {}

    @property
    def height(self):
        """Total y-space the widget occupies for layout purposes."""
        #Should be overridden in many cases, but we can make some
        #guesses about size that may be adequate
        if len(self.widgets) <= 0:
            if len(self.sprites) == 1:
                #If there are no widgets and just a single sprite, height
                #is PROBABLY the height of that sprite.
                if self.sprites[0].height is not None:
                    return self.sprites[0].height
                return 0
            else:
                #If there are multiple sprites, we have no reasonable way of
                #guessing the overall size, so raise an error if something
                #asks for the height and this isn't overridden
                raise NotImplementedError("Widget height not specified.")
        else:
            #Best guess is the total size taken by subwidgets in this layout
            if self.layoutStyle["arrangement"] == "horizontal":
                return max([widget.height for widget in self.widgets])
            elif self.layoutStyle["arrangement"] == "vertical":
                return sum([widget.height + self.layoutStyle["verticalPadding"] for widget in self.widgets])
            elif self.layoutStyle["arrangement"] == "grid":
                return self._rowPosition(0, self.activeRows[-1]+1)
            elif self.layoutStyle["arrangement"] == "none":
                return max([widget.height for widget in self.widgets])

    @property
    def width(self):
        """Total x-space the widget occupies for layout purposes."""
        #see height for logic explanation
        if len(self.widgets) <= 0:
            if len(self.sprites) == 1:
                if self.sprites[0].width is not None:
                    return self.sprites[0].width
                return 0
            else:
                raise NotImplementedError("Widget width not specified.")
        else:
            if self.layoutStyle["arrangement"] == "vertical":
                return max([widget.width for widget in self.widgets])
            elif self.layoutStyle["arrangement"] == "horizontal":
                return sum([widget.width + self.layoutStyle["horizontalPadding"] for widget in self.widgets])
            elif self.layoutStyle["arrangement"] == "grid":
                return self._columnPosition(self.activeColumns[-1]+1, 0)
            elif self.layoutStyle["arrangement"] == "none":
                return max([widget.width for widget in self.widgets])

    @property
    def anchorPosition(self):
        """Widget's base screen position."""
        return (self._anchorPosition[0] + self.internalPositionOffset[0],
                self._anchorPosition[1] + self.internalPositionOffset[1])

    def positionInBounds(self, x, y):
        """Returns True if x, y coordinates are within the widget's specified screen area."""
        return (x >= self.anchorPosition[0] and x < self.anchorPosition[0] + self.width and
                y >= self.anchorPosition[1] and y < self.anchorPosition[1] + self.height)

    @property
    def followCamera(self):
        return self._followCamera

    @followCamera.setter
    def followCamera(self, value):
        """Not only sets for this widget per se, but its subwidgets and sprites."""
        self._followCamera = value
        for sprite in self.sprites:
            sprite.follow_camera = value
        for widget in self.widgets:
            widget.followCamera = value

    @property
    def baseLayer(self):
        return self._baseLayer

    @baseLayer.setter
    def baseLayer(self, value):
        self._baseLayer = value
        for sprite in self.sprites:
            sprite.layer = self._baseLayer + sprite.layerOffset
        for widget in self.widgets:
            widget.baseLayer = self._baseLayer + widget.layerOffset

    @property
    def flow(self):
        if self.layoutStyle["reverseArrangement"]:
            return -1
        return 1

    def setPosition(self, x = None, y = None):
        """Change the widget's position along with all subwidgets and sprites."""
        if x == None:
            x = self._anchorPosition[0]
        if y == None:
            y = self._anchorPosition[1]
        self._anchorPosition = (x, y)
        self.positionWidgets()
        for sprite in self.sprites:
            sprite.setPos(self.anchorPosition[0] + self._spriteOffsets[sprite.unique_id][0],
                            self.anchorPosition[1] + self._spriteOffsets[sprite.unique_id][1])

    def update(self, *args, **kwargs):
        """Update this widget and its subwidgets if some change in the display is desired."""
        for widget in self.widgets:
            widget.update()

    def _gridRow(self, row):
        """Return all widgets in a row of the grid."""
        return [widget for widget in self.widgets if widget.layoutPosition is not None and widget.layoutPosition[1] == row]

    def _gridColumn(self, column):
        """Return all widgets in a column of the grid."""
        return [widget for widget in self.widgets if widget.layoutPosition is not None and widget.layoutPosition[0] == column]

    @property
    def activeRows(self):
        """Return all rows that contain at least one widget."""
        return sorted(list(set([widget.layoutPosition[1] for widget in self.widgets if widget.layoutPosition is not None])))

    @property
    def activeColumns(self):
        """Return all columns that contain at least one widget."""
        return sorted(list(set([widget.layoutPosition[0] for widget in self.widgets if widget.layoutPosition is not None])))

    def _widgetsInRow(self, row):
        """Return all widgets in this row."""
        return [widget for widget in self.widgets if widget.layoutPosition is not None and widget.layoutPosition[1] == row]

    def _widgetsInColumn(self, column):
        """Return all widgets in this column."""
        return [widget for widget in self.widgets if widget.layoutPosition is not None and widget.layoutPosition[0] == column]

    def _rowPosition(self, column, row):
        """Return the y-position of this row (/column pair if collapsed)."""
        offset = 0
        if not self.layoutStyle["collapseRows"]:
            for otherRow in self.activeRows:
                if otherRow < row:
                    offset += max([widget.height for widget in self._widgetsInRow(otherRow)]) + self.layoutStyle["verticalPadding"]
        else:
            for otherRow in self.activeRows:
                if otherRow < row:
                    offset += max([widget.height for widget in self._widgetsInRow(otherRow) if widget.layoutPosition[0] == column]) + self.layoutStyle["verticalPadding"]
        return offset

    def _columnPosition(self, column, row):
        """Return the x-position of this column (/row pair if collapsed)."""
        offset = 0
        if not self.layoutStyle["collapseColumns"]:
            for otherColumn in self.activeColumns:
                if otherColumn < column:
                    try:
                        offset += max([widget.width for widget in self._widgetsInColumn(otherColumn)]) + self.layoutStyle["horizontalPadding"]
                    except ValueError:
                        pass
        else:
            for otherColumn in self.activeColumns:
                if otherColumn < column:
                    try:
                        offset += max([widget.width for widget in self._widgetsInColumn(otherColumn) if widget.layoutPosition[1] == row]) + self.layoutStyle["horizontalPadding"]
                    except ValueError:
                        pass
        return offset

    def setLayoutStyle(self, arrangement = None, horizontalAlignment = None, verticalAlignment = None, horizontalPadding = None, verticalPadding = None, reverseArrangement = None, collapseColumns = None, collapseRows = None, explicitColumnSize = None, explicitRowSize = None):
        """Change aspects of the layout used by the widget (without immediately changing any positions)."""
        if arrangement is not None:
            self.layoutStyle["arrangement"] = arrangement
        if horizontalAlignment is not None:
            self.layoutStyle["horizontalAlignment"] = horizontalAlignment
        if verticalAlignment is not None:
            self.layoutStyle["verticalAlignment"] = verticalAlignment
        if horizontalPadding is not None:
            self.layoutStyle["horizontalPadding"] = horizontalPadding
        if verticalPadding is not None:
            self.layoutStyle["verticalPadding"] = verticalPadding
        if reverseArrangement is not None:
            self.layoutStyle["reverseArrangement"] = reverseArrangement
        if collapseColumns is not None:
            self.layoutStyle["collapseRows"] = collapseColumns
        if collapseRows is not None:
            self.layoutStyle["collapseColumns"] = collapseRows
        if explicitColumnSize is not None:
            self.layoutStyle["explicitColumnSize"] = explicitColumnSize
        if explicitRowSize is not None:
            self.layoutStyle["explicitRowSize"] = explicitRowSize

    def relativePosition(self, widget):
        if widget not in self.widgets:
            raise AttributeError("Widget %s is not a child of widget %s! Cannot get relative position." % (widget, self))
        return (widget.anchorPosition[0] - self.anchorPosition[0],
                widget.anchorPosition[1] - self.anchorPosition[1])

    def positionWidgets(self):
        """Reposition all subwidgets according to the layout."""
        if self.layoutStyle["arrangement"] == "vertical":
            self.widgets.sort(key=lambda widget: widget.layoutPosition or -1)
            y = 0
            for widget in self.widgets:
                if widget.layoutPosition is not None:
                    if self.layoutStyle["verticalAlignment"] == "bottom":
                        widget.setPosition(self.anchorPosition[0], self.anchorPosition[1] + y * self.flow)
                    elif self.layoutStyle["verticalAlignment"] == "top":
                        widget.setPosition(self.anchorPosition[0], self.anchorPosition[1] + self.height - (widget.height + y * self.flow))
                    if self.layoutStyle["explicitRowSize"] == None:
                        y += widget.height + self.layoutStyle["verticalPadding"]
                    else:
                        y += self.layoutStyle["explicitRowSize"]
        elif self.layoutStyle["arrangement"] == "horizontal":
            self.widgets.sort(key=lambda widget: widget.layoutPosition or -1)
            x = 0
            for widget in self.widgets:
                if widget.layoutPosition is not None:
                    if self.layoutStyle["horizontalAlignment"] == "left":
                        widget.setPosition(self.anchorPosition[0] + x * self.flow, self.anchorPosition[1])
                    elif self.layoutStyle["horizontalAlignment"] == "right":
                        widget.setPosition(self.anchorPosition[0] + self.width - (widget.width + x * self.flow), self.anchorPosition[1])
                    if self.layoutStyle["explicitColumnSize"] == None:
                        x += widget.width + self.layoutStyle["horizontalPadding"]
                    else:
                        x += self.layoutStyle["explicitColumnSize"]
        elif self.layoutStyle["arrangement"] == "grid":
            columnPositions = {}
            rowPositions = {}
            if self.layoutStyle["explicitColumnSize"] == None:
                if not self.layoutStyle["collapseColumns"]:
                    columnPositions = dict([(column, self._columnPosition(column, None)) for column in self.activeColumns])
            else:
                columnPositions = dict([(column, column * self.layoutStyle["explicitColumnSize"]) for column in self.activeColumns])
            if self.layoutStyle["explicitRowSize"] == None:
                if not self.layoutStyle["collapseRows"]:
                    rowPositions = dict([(row, self._rowPosition(None, row)) for row in self.activeRows])
            else:
                rowPositions = dict([(row, row * self.layoutStyle["explicitRowSize"]) for row in self.activeRows])
            for widget in self.widgets:
                if widget.layoutPosition is not None:
                    if widget.layoutPosition[0] in columnPositions:
                        xoffset = columnPositions[widget.layoutPosition[0]]
                    else:
                        xoffset = self._columnPosition(*widget.layoutPosition)
                    if widget.layoutPosition[1] in rowPositions:
                        yoffset = rowPositions[widget.layoutPosition[1]]
                    else:
                        yoffset = self._rowPosition(*widget.layoutPosition)
                    widget.setPosition(self.anchorPosition[0] + xoffset, self.anchorPosition[1] + yoffset * self.flow)
        elif self.layoutStyle["arrangement"] == "none":
            for widget in self.widgets:
                widget.setPosition(self.anchorPosition[0], self.anchorPosition[1])


    def addWidget(self, widget, layoutPosition=None, suppressCameraInheritance=False, layerOffset=1, relativePosition=None):
        """Add a subwidget to this widget."""
        self.widgets.append(widget)
        widget.layoutPosition = layoutPosition
        if not suppressCameraInheritance:
            widget.followCamera = self.followCamera
        widget.layerOffset = layerOffset
        widget.baseLayer = self.baseLayer + layerOffset
        if relativePosition is not None:
            widget.setPosition(self.anchorPosition[0] + relativePosition[0], self.anchorPosition[1] + relativePosition[1])
        return widget

    def addSprite(self, sprite, relativePosition=(0, 0), layerOffset=0):
        """Add a sprite to this widget."""
        self.sprites.append(sprite)
        self._spriteOffsets[sprite.unique_id] = relativePosition
        registerSprite(sprite)
        if self.followCamera:
            sprite.follow_camera = True
        sprite.setPos(self.anchorPosition[0] + relativePosition[0], self.anchorPosition[1] + relativePosition[1])
        sprite.layerOffset = layerOffset
        sprite.layer = self.baseLayer + layerOffset
        sprite.flip = self.flipSprites[:]
        return sprite

    def listen(self, key, listener, priority=0):
        addCustomListener(key, listener, priority=priority)
        self._custom_listeners[key] = listener

    def destroyWidget(self, widget):
        widget.destroy()
        self.widgets.remove(widget)

    def show(self):
        """Toggle the display of this widget and its subwidgets on."""
        self.hidden = False
        self._changeSpritesVisibility(not self.hidden)
        for widget in self.widgets:
            widget.show()

    def hide(self):
        """Toggle the display of this widget and its subwidgets off."""
        self.hidden = True
        self._changeSpritesVisibility(not self.hidden)
        for widget in self.widgets:
            widget.hide()

    def _changeSpritesVisibility(self, val):
        deadSprites = []
        for sprite in self.sprites:
            try:
                sprite.show = val
            except ObjectDestroyedError:
                deadSprites.append(sprite)
        for sprite in deadSprites:
            self.sprites.remove(sprite)

    def _destroySpritesSelfOnly(self):
        for sprite in self.sprites:
            removeSprite(sprite)
        self.sprites = []
        self._spriteOffsets = {}

    def destroySprites(self):
        """Clear sprites from this widget and its subwidgets."""
        self._destroySpritesSelfOnly()
        for widget in self.widgets:
            widget.destroySprites()

    def destroyWidgets(self):
        """Destroy all subwidgets of this widget."""
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []

    def destroy(self):
        """Clear sprites, listeners, and references from this widget and all subwidgets and prepare for destruction."""
        self.being_destroyed = True
        self._destroySpritesSelfOnly()
        self.destroyWidgets()
        for key, listener in self._custom_listeners.items():
            removeCustomListener(key, listener)
        self._custom_listeners = {}

    def setAlpha(self, alpha):
        """Set alpha value for all sprites in this widget and its subwidgets."""
        for sprite in self.sprites:
            sprite.alpha = alpha
        for widget in self.widgets:
            widget.setAlpha(alpha)

class SpacerWidget(InterfaceWidget):

    """Helps with layout positioning by occupying space."""

    def __init__(self, width=0, height=0, *args, **kwargs):
        super(SpacerWidget, self).__init__(*args, **kwargs)
        self._width = width
        self._height = height

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

class FadeWidget(InterfaceWidget):

    def __init__(self, style="simple", color=COLOR_BLACK, startFaded=False, *args, **kwargs):
        super(FadeWidget, self).__init__(followCamera=True, *args, **kwargs)
        self.style = style
        self.faders = []
        if style == "simple":
            self.fader = self.addSprite(makeSprite((WIDGET_PATH, "darkener.png")))
            self.fader.set_dimensions(*getWindowDimensionsScaled())
            if not startFaded:
                self.fader.alpha = 0
        elif style == "sweep":
            self.fader = self.addSprite(makeSprite((WIDGET_PATH, "fade_sweep.png")))
            self.fader.set_dimensions(getWindowDimensionsScaled()[0]*3, getWindowDimensionsScaled()[1])
            if not startFaded:
                self.fader.setPos(-2*getWindowDimensionsScaled()[0], 0)
            else:
                #TODO: check if this is actually the right position to start
                self.fader.setPos(-1*getWindowDimensionsScaled()[0], 0)
        elif style == "diamond":
            self.fader = self.addSprite(makeSprite((WIDGET_PATH, "fade_diamond.png")))
            self.fader.set_dimensions(1, 1)
            self.fader.setPos(getWindowDimensionsScaled()[0]/2, getWindowDimensionsScaled()[1]/2)
            self.fader.setCenter(True, True)
        elif style == "dissolve":
            for i in range(4):
                fader = self.addSprite(makeSprite((WIDGET_PATH, "dissolve_fade_%s.png" % str(i+1))))
                fader.size = [getWindowDimensionsScaled()[0]/4+1, getWindowDimensionsScaled()[1]/4+1]
                fader.tile_texture()
                fader.layer = FADE_LAYER
                if not startFaded:
                    fader.show = False
                self.faders.append(fader)
        if style != "dissolve":
            self.fader.layer = FADE_LAYER
        if style == "simple" or style == "sweep":
            self.fader.setColor(*color)
        self.faderFlag = False

    def update(self, time=1.0, fadingIn=False, *args, **kwargs):
        if not fadingIn:
            if self.style == "simple":
                self.fader.alpha = 1.0 - time
            elif self.style == "sweep":
                self.fader.setPos((-3*(time)*getWindowDimensionsScaled()[0])-getWindowDimensionsScaled()[0], 0)
            elif self.style == "diamond":
                if not self.faderFlag:
                    if time > 0.04:
                        self.fader.set_dimensions(int(getWindowDimensionsScaled()[0]*2.25*(1.0-time)),
                                                    int(getWindowDimensionsScaled()[1]*2.25*(1.0-time)))
                    else:
                        self.faderFlag = True
                        removeSprite(self.fader)
                        self.faders = [makeSprite((WIDGET_PATH, "fade_diamond_"+spath+".png")) for spath in ("ul", "ur", "bl", "br")]
                        for fader in self.faders:
                            fader.layer = FADE_LAYER
            elif self.style == "dissolve":
                if time < 0.25:
                    self.faders[3].show = True
                if time < 0.5:
                    self.faders[2].show = True
                if time < 0.75:
                    self.faders[1].show = True
                if time < 0.99:
                    self.faders[0].show = True
        else:
            if self.style == "simple":
                self.fader.alpha = time
            elif self.style == "sweep":
                self.fader.setPos((3*(1.0 - time)*getWindowDimensionsScaled()[0])-getWindowDimensionsScaled()[0], 0)
            elif self.style == "diamond":
                if len(self.faders) == 0:
                    self.faderFlag = True
                    removeSprite(self.fader)
                    self.faders = [makeSprite((WIDGET_PATH, "fade_diamond_"+spath+".png")) for spath in ("ul", "ur", "bl", "br")]
                    for fader in self.faders:
                        fader.layer = FADE_LAYER
                widthDistance = getWindowDimensionsScaled()[0]/2
                heightDistance = getWindowDimensionsScaled()[1]/2
                self.faders[0].setPos(-1*widthDistance*(1.0-time), heightDistance*(1.0-time))
                self.faders[1].setPos(widthDistance*(1.0-time), heightDistance*(1.0-time))
                self.faders[2].setPos(-1*widthDistance*(1.0-time), -1*heightDistance*(1.0-time))
                self.faders[3].setPos(widthDistance*(1.0-time), -1*heightDistance*(1.0-time))
            elif self.style == "dissolve":
                if time < 0.01:
                    self.faders[3].show = False
                if time < 0.25:
                    self.faders[2].show = False
                if time < 0.5:
                    self.faders[1].show = False
                if time < 0.75:
                    self.faders[0].show = False
