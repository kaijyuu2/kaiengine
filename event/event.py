
from kaiengine.debug import debugMessage
import traceback

class Event(object):

    __slots__ = ['listener', 'priority', 'delete_me']

    def __init__(self, listener, priority = 0):
        self.listener = listener
        self.priority = priority
        self.delete_me = False

    def call_listener(self, *args, **kwargs):
        try:
            return self.listener(*args, **kwargs)
        except Exception as e:
            debugMessage(traceback.format_exc())
            debugMessage("something broke with an event listener; deleting it")
            debugMessage(e)
            self.delete_me = True

    def get_priority(self):
        if callable(self.priority):
            return self.priority()
        return self.priority
