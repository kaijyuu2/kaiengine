#special object for countable bool
#super bool!

#"force" is for when we don't want to count "below" or "above" true or false
#so if force is set to true, no matter how many falses are set, the counter won't go below 0
#similarly if force is set to false, no matter how many trues are set, the counter won't go above 1
#most of the time, one or the other is likely going to be set

class sBool(object):
    def __init__(self, val = False, force = None):
        self.counter = 0
        self.force = force
        self.initial_val = val
        
        if val is True:
            self.counter = 1
            
    def set(self, val):
        if val:
            self.counter += 1
        else:
            self.counter -= 1
        if self.force is True:
            if self.counter < 0:
                self.counter = 0
        elif self.force is False:
            if self.counter > 1:
                self.counter = 1
                
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
            
        