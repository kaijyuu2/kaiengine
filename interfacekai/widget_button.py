

from .interfaceWidget import InterfaceWidget
from .widget_label import LabelWidget


class ButtonWidget(InterfaceWidget):
    def __init__(self, owner, index,  bg = None, text = " ", width = None, height = None, *args, **kwargs):
        super(ButtonWidget, self).__init__(owner, index, *args, **kwargs)
        if bg is not None:
            self.setSprite(bg)
        self.setWidgetDimensions(width, height)
        self.label_index = self.addWidget(LabelWidget, text = text)
        self.widgets[self.label_index].setSpriteCenter(True,True)
        self.updateLabelCenter()

    def updateLabelCenter(self):
        try:
            self.widgets[self.label_index].SetLayoutOffset(self.width/2, self.height/2)
        except (KeyError, AttributeError):
            pass

    def setWidgetDimensions(self, *args, **kwargs):
        super(ButtonWidget, self).setWidgetDimensions(*args, **kwargs)
        self.updateLabelCenter()

    def setText(self, *args, **kwargs):
        self.widgets[self.label_index].setText(*args, **kwargs)

    def getText(self):
        return self.widgets[self.label_index].getText()

    def getTextSet(self):
        return self.widgets[self.label_index].getTextSet()

    def setFontSize(self, *args, **kwargs):
        self.widgets[self.label_index].setFontSize(*args, **kwargs)

    def setFont(self, *args, **kwargs):
        self.widgets[self.label_index].setFont(*args, **kwargs)
