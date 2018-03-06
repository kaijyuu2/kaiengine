

import weakref

def weakRef(obj):
    """returns a weakref of the object if possible. If already a weakref instance, just returns itself"""
    try: obj = weakref.ref(obj)
    except: pass
    return obj

def unWeakRef(obj):
    """unweakrefs a weakref object. If not a weakref object, just return itself"""
    if isinstance(obj, weakref.ref):
        obj = obj()
    return obj
