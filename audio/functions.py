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

def _basicFunc(*args, **kwargs):
    return None

for name in func_names:
    globals()[name] = _basicFunc

def initAudio():
    try:
        from . import sdAudio
        sdAudio.initAudio()
        for name in func_names:
            globals()[name] = getattr(sdAudio, name)
    except Exception as e:
        debugMessage("WARNING: Couldn't initialize any audio backend; sound disabled")
        debugMessage(e)

