

from .interfaceWidget import InterfaceWidget
from kaiengine.display import createLabel

from kaiengine.gconfig import *


class LabelWidget(InterfaceWidget):
    def __init__(self, owner, index, text = None, *args, **kwargs):
        super(LabelWidget, self).__init__(owner, index, *args, **kwargs)
        self._justification = LABEL_JUSTIFICATION_LEFT
        self._font_size = DEFAULT_TEXT_SIZE
        self._font = DEFAULT_FONT
        self._text = None
        self.setText(text)

    def setText(self, text, font_size = None, font = None):
        if font_size is None:
            font_size = self._font_size
        if font is None:
            font = self._font
        if text is not None:
            text = str(text)
            if text != self._text:
                if self.sprite is None:
                    self.setSprite(createLabel(text, font_size, font, show = not self.widget_hidden))
                else:
                    self.sprite.setText(text, font_size, font)
                self._font = font
                self._font_size = font_size
                self._text = text
                self._updateJustification()
                self._updateWidgetDimensions()
        if font_size != self._font_size:
            if self.sprite is not None:
                self.sprite.setFontSize(font_size)
            self._font_size = font_size
            self._updateJustification()
            self._updateWidgetDimensions()
        if font != self._font:
            if self.sprite is not None:
                self.sprite.setFont(font)
            self._font = font
            self._updateJustification()
            self._updateWidgetDimensions()

    def getText(self):
        return self._text

    def getTextSet(self):
        return self.getText() != None

    def setFontSize(self, font_size):
        if self.sprite is not None:
            self.sprite.SetFontSize(font_size)
            self._updateWidgetDimensions()
        self._font_size = font_size

    def setFont(self, font):
        if self.sprite is not None:
            self.sprite.setFont(font)
            self._updateWidgetDimensions()
        self._font = font

    def setJustification(self, justification):
        self._justification = justification
        self._updateJustification()

    def _updateJustification(self):
        if not self.getSpriteCenter()[0] and self._justification == LABEL_JUSTIFICATION_RIGHT:
            try: self.setSpriteOffset(x = -self.sprite.width)
            except AttributeError: self.setSpriteOffset(x = 0)
        else:
            self.setSpriteOffset(x = 0)

    def _updateWidgetDimensions(self):
        self.setWidgetDimensions(*self.getSpriteDimensions())
