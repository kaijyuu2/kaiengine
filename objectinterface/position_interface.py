

from kaiengine.destroyinterface import DestroyInterface
from kaiengine.coordinate import Coordinate

def _interpretPositionArgs(*args, **kwargs):
    try: args[0].__iter__
    except (AttributeError, IndexError): pass
    else: args = args[0]
    if kwargs:
        try: args[0] = kwargs["x"]
        except KeyError: pass
        try:
            newy = kwargs["y"]
            args = args + [None]*(2 - len(args))
            args[1] = newy
        except KeyError:
            pass
        try:
            newz = kwargs["z"]
            args = args + [None]*(3 - len(args))
            args[2] = newz
        except KeyError:
            pass
    return args

class PositionInterface(DestroyInterface):
    def __init__(self, *args, **kwargs):
        super(PositionInterface, self).__init__(*args, **kwargs)
        self._pos = Coordinate((0.0,0.0))

    @property
    def pos(self):
        return self.getPos()
    @pos.setter
    def pos(self, val):
        self.setPos(val)


    def setPos(self, *args, **kwargs):
        newargs = _interpretPositionArgs(*args, **kwargs)
        for i, arg in enumerate(newargs):
            if arg is None:
                try:
                    newargs[i] = self._pos[i]
                except IndexError:
                    newargs[i] = 0
        newargs = newargs + self._pos[len(newargs):]
        self._pos = Coordinate(newargs)

    def movePos(self, *args, **kwargs):
        newargs = _interpretPositionArgs(*args, **kwargs)
        for i, arg in enumerate(newargs):
            if arg is None:
                newargs[i] = 0
        self.setPos(self.pos + newargs)

    def getPos(self):
        return self._pos
