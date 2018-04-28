
from kaiengine.debug import debugMessage


'''Interface object for the destroy method'''

class DestroyInterface(object):
    def __init__(self, *args, **kwargs):
        self._destroyed = False
        try: super().__init__(*args, **kwargs)
        except TypeError: pass #if too many parameters passed, just skip error


    @property
    def destroyed(self):
        return self._destroyed
    @destroyed.setter
    @property
    def destroyed(self, val):
        debugMessage("destroyed cannot be set outside of the destroy() method.")

    def destroy(self):
        self._destroyed = True
        try: super().destroy
        except (AttributeError, TypeError): pass
        else: super().destroy()


    def __del__(self):
        self.destroy()
