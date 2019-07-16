
# special dict object

class sDict(dict):
    def __init__(self, oldDict = None):
        super().__init__()
        self.counter = 0
        self.sorted_keys = []
        if oldDict:
            try:
                self.counter = oldDict.counter
            except:
                pass
            self.update(oldDict)

    def append(self, newValue):
        if len(self.sorted_keys) > 250:
            self.purify()
        self[self.counter] = newValue
        self.sorted_keys.append(self.counter)
        self.counter += 1
        return self.counter - 1

    def extend(self, newList):
        for item in newList:
            self.append(item)

    def length(self):
        return self.counter

    def last_key(self):
        return sorted(self.keys())[-1]

    def last_item(self):
        return self[self.last_key()]

    def firstKey(self):
        return sorted(self.keys())[0]

    def firstItem(self):
        return self[self.firstKey()]

    def purify(self):
        self.sorted_keys = sorted([key for key in self.keys()])

    def clear(self):
        super().clear()
        self.counter = 0

    def update(self, *args, **kwargs):
        #make update return a reference to itself. Fixes one thing I didn't like about the base dict object
        super().update(*args, **kwargs)
        return self
