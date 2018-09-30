from kaiengine.event import ListenerRegistryMeta
from .interfaceElementEvent import on_event, on_activate

class _EventDefHandler(type):

    """Makes special event decorators available in class scope for convenience."""

    class _EventHandlerDict(dict):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self["on_activate"] = on_activate
            self["on_event"] = on_event

        def __setitem__(self, key, value):
            try:
                value._special_key_append
            except AttributeError:
                pass
            else:
                key = key + value._special_key_append
            dict.__setitem__(self, key, value)

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return _EventDefHandler._EventHandlerDict()

class _InterfaceElementMeta(_EventDefHandler, ListenerRegistryMeta):

    """Combines desired metaclasses since we can only inherit from one."""

    pass
