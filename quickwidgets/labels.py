# -*- coding: utf-8 -*-

from kaiengine.gconfig import KAI_MONO3_DARK_FONT
from kaiengine.interface import ScreenElement
from kaiengine.label import Label


class LabelElement(ScreenElement):
    def __init__(self, text = None, font = None, font_size = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if font is None:
            font = KAI_MONO3_DARK_FONT #set new default
        self.setSprite(Label(""))
        if font:
            self.setFont(font)
        if text:
            self.setText(text, font_size = font_size)
            
        
    def setText(self, *args, **kwargs):
        self.getSprite().setText(*args, **kwargs)
        
    def setFont(self, *args, **kwargs):
        self.getSprite().setFont(*args, **kwargs)
        