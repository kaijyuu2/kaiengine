# -*- coding: utf-8 -*-

from kaiengine.destroyinterface import DestroyInterface

INTERFACE_DRIVER_SLEEP_KEY = "_INTERFACE_DRIVER_SLEEP_NOT_TOP_LEVEL"



_topElements = []

def pushTopElement(newelement):
    if len(_topElements) > 0:
        newlayer = _topElements[-1].getMaxLayer() + 1
        _topElements[-1].sleep(INTERFACE_DRIVER_SLEEP_KEY)
    else:
        newlayer = 0
    _topElements.append(newelement)
    newelement.setLayer(newlayer)
    newelement._gainFocus()
    return newelement

def popTopElement():
    try:
        oldelement = _topElements.pop()
        oldelement.destroy()
        try:
            _topElements[-1].wakeUp(INTERFACE_DRIVER_SLEEP_KEY)
        except IndexError:
            pass
    except IndexError:
        pass

def closeAllElements():
    for element in _topElements:
        element.destroy()
    _topElements.clear()
