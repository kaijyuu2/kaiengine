# -*- coding: utf-8 -*-

#an abberation to all that is holy

"""
syntax:


try: smr(VALUE)
except sm[value1]:
    ...
except sm[value2]:
    ...
except SM_DEFAULT:
    default behavior


SM_DEFAULT will only catch unhandled state machine states, not other errors, so you can still catch those in separate blocks
Also make sure your value is something hashable, or a similar problem will occur. check for TypeError if you want to catch that.
a final except block is also required else it'll raise an exception instead of doing nothing (just have except: pass).

this is the minimum boilerplate I could come up with
"""

from collections import defaultdict

class SM_DEFAULT(Exception):
    def __call__(self):
        class NewStateMachineException(SM_DEFAULT):
            pass
        return NewStateMachineException

sm = defaultdict(SM_DEFAULT())

def smr(val):
    raise sm[val]
