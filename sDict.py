
# special dict object

class sDict(dict):
    def __init__(self, oldDict = None):
        super(sDict, self).__init__()
        self.counter = 0
        self.sorted_keys = []
        if oldDict:
            try:
                self.counter = oldDict.counter
            except:
                pass
            self.update(oldDict)

    def append(self, newValue):
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
        keys = list(self.keys())
        keys.sort()
        return keys[-1]

    def last_item(self):
        return self[self.last_key()]

    def clear(self):
        try: #error suppression on game close
            super(sDict, self).clear()
        except TypeError:
            pass
        self.counter = 0

    def update(self, newdict):
        #make update return a reference to itself. Fixes one thing I didn't like about the base dict object
        super(sDict, self).update(newdict)
        return self
