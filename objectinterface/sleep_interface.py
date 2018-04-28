# -*- coding: utf-8 -*-


class SleepInterface():
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleeping = False
    
    
    def sleep(self):
        self.sleeping = True
        
    def wakeUp(self):
        self.sleeping = False