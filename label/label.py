


'''container object for labels.'''

from kaiengine.gconfig import *
import os
from kaiengine.container import Container
from kaiengine.baseobject import BaseObject
from kaiengine.objectdestroyederror import ObjectDestroyedError
from kaiengine.uidgen import GenerateUniqueID
from kaiengine.fonts import FontTypeError
from kaiengine.debug import debugMessage

from .label_ttf import Label_TTF
from .label_graphic import Label_Graphic
from .label_graphic2 import LabelGraphic2

LABEL_ID = "LABEL"

class Label(Container, BaseObject):
    def __init__(self, text, font_size = None, font = None, color = None, layer = None, show = True, *args, **kwargs):
        super(Label, self).__init__()
        self._unique_id = GenerateUniqueID(LABEL_ID)
        self._sublabel = None
        self.setupContainer("_sublabel")
        if color is None:
            color = DEFAULT_TEXT_COLOR
        if font_size is None:
            font_size = DEFAULT_TEXT_SIZE
        self._SetupSublabel(text, font_size, font, color, layer, show, *args, **kwargs)

    @property
    def unique_id(self):
        return self._unique_id
    @unique_id.setter
    def unique_id(self, val):
        debugMessage("unique id in labels not settable")


    def setText(self, text, font_size = None, font = None, color = None, layer = None):
        self._sublabel.set_text(text, font_size, font, color)
        if layer is not None:
            self._sublabel.layer = layer

    def setFont(self, font):
        self._SetupSublabel(font = font)

    def _SetupSublabel(self, *args, **kwargs):
        try: font = kwargs["font"]
        except KeyError:
            try: font = args[2]
            except IndexError: raise TypeError("Missing 'font' keyword")
        oldfont = self._GetSublabelFont()
        if font is None:
            if oldfont is None:
                font = DEFAULT_FONT
            else:
                font = oldfont
        if "font" in kwargs:
            kwargs["font"] = font
        elif len(args) >= 3:
            args = list(args)
            args[2] = font
        ext = os.path.splitext(font)[1]
        if oldfont is None or ext != os.path.splitext(oldfont)[1]:
            tempdata = self._GetSublabelData()
            self._RemoveSublabel()
            if ext == TTF_EXTENSION:
                self._sublabel = Label_TTF(*args, **kwargs)
            elif ext == GRAPHIC_FONT_EXTENSION:
                self._sublabel = Label_Graphic(*args, **kwargs)
            elif ext == GRAPHIC_FONT_2_EXTENSION:
                self._sublabel = LabelGraphic2(*args, **kwargs)
            elif ext == GRAPHIC_FONT_3_EXTENSION:
                self._sublabel = LabelGraphic2(*args, **kwargs)
            else:
                if len(ext) == 0:
                    raise FontTypeError("No font type specified. Include the extension to fix.")
                raise FontTypeError("Invalid font type: " + ext)
            self._sublabel.updateLabelData(tempdata)
        else:
            self._sublabel.set_font(font)
        return font


    def _RemoveSublabel(self):
        if self._sublabel is not None:
            self._sublabel.destroy()
            self._sublabel = None

    def _GetSublabelFont(self):
        try:
            return self._sublabel.font
        except AttributeError:
            return None

    def _GetSublabelData(self):
        try:
            self._sublabel.getLabelData
        except AttributeError:
            return {}
        else:
            return self._sublabel.getLabelData()

    def destroy(self):
        self._RemoveSublabel()
        if Label:
            super(Label, self).destroy()
