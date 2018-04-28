# -*- coding: utf-8 -*-

from kaiengine.destroyinterface import DestroyInterface

SLEEP_KEY = "_DEFAULT_SLEEP_KEY"

class SleepInterface(DestroyInterface):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleeping = set()
    
    
    def sleep(self, key = SLEEP_KEY):
        self.sleeping.add(key)
        
    def wakeUp(self, key = SLEEP_KEY):
        self.sleeping.discard(key)