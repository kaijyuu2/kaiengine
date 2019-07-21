# -*- coding: utf-8 -*-

from kaiengine.debug import debugMessage

func_names = [name for template in ("play{}",
                                    "any{}Playing",
                                    "pause{}",
                                    "resume{}",
                                    "stop{}",
                                    "stop{}File",
                                    "set{}Volume",
                                    "get{}Volume",
                                    "disable{}",
                                    "enable{}",
                                    "toggle{}") for name in [template.format(variant) for variant in ("Audio", "Sound", "Music")]]

try:
    from . import sdAudio
    for name in func_names:
        globals()[name] = getattr(sdAudio, name)
except Exception as e:
    debugMessage("WARNING: Couldn't initialize sounddevice audio.")
    debugMessage(e)
    def _nop(*args, **kwargs):
        return None
    for name in func_names:
        globals()[name] = _nop

def initAudio():
    try:
        sdAudio
    except NameError:
        pass
    else:
        sdAudio.initAudio()
