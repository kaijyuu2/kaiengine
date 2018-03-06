
from collections import OrderedDict

class rDict(OrderedDict):

    def __init__(self):
        super(rDict, self).__init__()
        self._reverse = {}

    def update(self, item, key):
        '''Adds an element to the rDict.'''
        try:
            self[self._reverse[item]].remove(item)
            if len(self[self._reverse[item]]) < 1:
                del self[self._reverse[item]]
        except KeyError:
            pass
        try:
            self[key].append(item)
        except KeyError:
            self[key] = [item]
        self._reverse[item] = key

    def aUpdate(self, item, change):
        '''Adds an element to the rDict with an offset to the current key instead of a fixed key.'''
        try:
            key = self._reverse[item]+change
        except KeyError:
            key = change
        self.update(item, key)

    def abilityUpdate(self, item, item2, change):
        '''Adds an element based on a current item, but with a tuple element item2 appended to the final updated version, and changes nothing if there's already a higher ranked combined tuple.'''
        combined = (item[0], item[1], item2)
        try:
            key = self._reverse[item]+change
        except KeyError:
            key = change
        try:
            if self._reverse[combined] >= key:
                return
        except KeyError:
            pass
        self.update(combined, key)

    def itemPresent(self, item):
        '''Checks if an item is present somewhere in the dict.'''
        return item in self._reverse
