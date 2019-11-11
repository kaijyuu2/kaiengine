#special object for countable bool
#super bool!

#"minimum"/"maximum" are for when we don't want to count "below" or "above" true or false
#so if minimum is set to false, no matter how many falses are set, the counter won't go below 0 (false)
#similarly if maximum is set to true, no matter how many trues are set, the counter won't go above 1 (true)
#most of the time, one or the other is likely going to be set

class sBool(object):
    def __init__(self, val = False, minimum = None, maximum = None):
        self.counter = 0
        self.initial_val = val
        if minimum is not None:
            if maximum is not None:
                def _clamp(self, mn=minimum, mx=maximum):
                    self.counter = max(mn, min(self.counter, mx))
            else:
                def _clamp(self, mn=minimum):
                    self.counter = max(mn, self.counter)
        elif maximum is not None:
            def _clamp(self, mx=maximum):
                self.counter = min(self.counter, mx)
        else:
            def _clamp(self):
                return
        self.clamp = _clamp

        if val is True:
            self.counter = 1

    def set(self, val):
        if val:
            self.counter += 1
        else:
            self.counter -= 1
        self.clamp()

    def check(self):
        return self.counter > 0

    def reset(self, val = None):
        if val is None:
            val = self.initial_val
        else:
            self.initial_val = val
        if val:
            self.counter = 1
        else:
            self.counter = 0
