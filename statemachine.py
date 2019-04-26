# -*- coding: utf-8 -*-

#an abberation to all that is holy

"""
syntax:


try: smr(VALUE)
except sm(value1):
    ...
except sm(value2):
    ...
except SM_DEFAULT:
    default behavior

note that this will catch errors in the smr call if you're doing anything there (ie, smr(1/0)). perhaps have an internal try/except block if that's a concern
also make sure your value is something hashable, or a similar problem will occur. check for TypeError if you want to catch that.
a final except block is also required else it'll raise an exception instead of doing nothing (just have "except SM_DEFAULT: pass", or "except: pass").
make sure SM_DEFAULT is after all your regular cases, else it will be used instead of them. python evaluates from top to bottom and stops at the first valid exception
SM_DEFAULT will only catch unhandled state machine states, not other errors, so you can still catch those in separate blocks

this is the minimum boilerplate I could come up with
"""

from collections import defaultdict

class _StateMachineDict(defaultdict):
    def __call__(self, key):
        return self[key]

class SM_DEFAULT(Exception):
    def __call__(self):
        class NewStateMachineException(SM_DEFAULT):
            pass
        return NewStateMachineException

sm = _StateMachineDict(SM_DEFAULT())

def smr(val):
    raise sm[val]
