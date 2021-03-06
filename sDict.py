
# special dict object

class sDict(dict):
    def __init__(self, old_dict = None):
        super().__init__()
        self.counter = 0
        if old_dict:
            try:
                self.counter = old_dict.counter
            except AttributeError:
                pass
            self.update(old_dict)

    @property
    def sorted_keys(self):
        return sorted(self.keys())

    def append(self, newValue):
        self[self.counter] = newValue
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

    def clear(self):
        super().clear()
        self.counter = 0

    def update(self, *args, **kwargs):
        #make update return a reference to itself. Fixes one thing I didn't like about the base dict object
        super().update(*args, **kwargs)
        return self
