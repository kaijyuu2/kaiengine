

from kaiengine.fonts import FontTypeError

class Label_Base(object):
    '''parent class for all label objects, other than the "label" container'''


    def __init__(self, text, font_size, font, color, layer, bordered = False, *args, **kwargs):
        super(Label_Base, self).__init__(*args, **kwargs)
        self.text = text
        self.font_size = font_size
        self.font = font
        self.color = color
        self.layer = layer
        self.bordered = bordered

    def getLabelData(self):
        #get data for transfer to another label type
        datakeys = ["text", "font", "color",
                "font_size", "layer", "follow_camera",
                "pos", "offset", "other_offsets", "size",
                "alpha", "show","center", "flip", "bordered"]
        returnvalue = {}
        for key in datakeys:
            try: returnvalue[key] = getattr(self, key)
            except AttributeError: pass
        return returnvalue

    def updateLabelData(self, *args, **kwargs):
        self.updateLabelData(*args, **kwargs)

    def updateLabelData(self, data):
        #update this label with data from a previous label type
        if len(data) > 0:
            for key, val in list(data.items()):
                try:
                    setattr(self, key, val)
                except FontTypeError:
                    pass
            self._set_text() #restore text graphics
