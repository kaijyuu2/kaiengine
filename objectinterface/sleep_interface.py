# -*- coding: utf-8 -*-

from kaiengine.destroyinterface import DestroyInterface

SLEEP_KEY = "_DEFAULT_SLEEP_KEY"

class SleepInterface(DestroyInterface):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleeping = set()


    def sleep(self, key = SLEEP_KEY):
        started_sleeping = len(self.sleeping) == 0
        self.sleeping.add(key)
        return started_sleeping

    def wakeUp(self, key = SLEEP_KEY):
        previouslysleeping = len(self.sleeping) != 0
        self.sleeping.discard(key)
        return previouslysleeping and not self.sleeping
