

from kaiengine.destroyinterface import DestroyInterface


class PositionInterface(DestroyInterface):
    def __init__(self, *args, **kwargs):
        super(PositionInterface, self).__init__(*args, **kwargs)
        self._pos = (0.0,0.0)

    @property
    def pos(self):
        return self.getPos()
    @pos.setter
    def pos(self, val):
        self.setPos(*val)

    def setPos(self, *args, **kwargs):
        self.setPos(*args, **kwargs)

    def setPos(self, x = None, y = None):
        if x is None: x = self._pos[0]
        if y is None: y = self._pos[1]
        self._pos = (float(x),float(y)) #made a tuple so that "self.pos[0] = something" won't work, enforcing use of setPos

    def movePos(self, x = 0, y = 0):
        self.setPos(self.pos[0] + x, self.pos[1] + y)

    def getPos(self, *args, **kwargs):
        return self.getPos(*args, **kwargs)

    def getPos(self):
        return self._pos

