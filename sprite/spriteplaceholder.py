

"""This exists solely to hold sprite textures for pre-loading.
Has none of the features of a regular sprite and will not display anything if you try"""

from kaiengine import sGraphics


class SpritePlaceholder(sGraphics.sSprite):
    def set_image(self, path, *args, **kwargs):
        try: del kwargs["display"] #remove the display keyword if it exists
        except KeyError: pass
        super(SpritePlaceholder, self).set_image(path, *args, display = False, **kwargs)
