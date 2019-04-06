# -*- coding: utf-8 -*-

#an abberation to all that is holy

"""
syntax:
    
    
try: smr(VALUE)
except sm(value1):
    ...
except sm(value2):
    ...
except:
    default behavior
    
    

note that this will catch errors in the smr call if you're doing anything there (ie, smr(1/0) would run the final except block, probably unintentionally). perhaps have an internal try/except block if that's a concern
also make sure your value is something hashable, or a similar problem will occur. check for TypeError if you want to catch that.
a final except block is also required else it'll crash instead of doing nothing (just have except: pass).

this is the minimum boilerplate I could come up with
"""

_state_machine_classes = {}

def _generateStateMachineClass(val):
    class new_state_machine_class(Exception):
        pass
    return new_state_machine_class

def sm(val):
    try:
        return _state_machine_classes[val]
    except KeyError:
        _state_machine_classes[val] = _generateStateMachineClass(val)
        return _state_machine_classes[val]
    
    
def smr(val):
    raise sm(val)
    