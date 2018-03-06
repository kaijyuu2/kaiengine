# -*- coding: utf-8 -*-

from kaiengine.debug import debugMessage

#enum
FUNC_PLAY_SOUND = 0
FUNC_PLAY_MUSIC = 1
FUNC_STOP_SOUNDS = 2
FUNC_STOP_MUSIC = 3
FUNC_SET_SOUND_VOLUME = 4
FUNC_SET_MUSIC_VOLUME = 5
FUNC_GET_SOUND_VOLUME = 6
FUNC_GET_MUSIC_VOLUME = 7
FUNC_TOGGLE_SOUND = 8
FUNC_TOGGLE_MUSIC = 9
FUNC_PLAY_WITH_INTRO = 10
FUNC_PRELOAD_MUSIC = 11
FUNC_PRELOAD_SOUND = 12
FUNC_ANY_SOUND_PLAYING = 13

_funcs = {}

def _basicFunc(*args, **kwargs):
    return None

def playSound(*args, **kwargs):
    return _funcs.get(FUNC_PLAY_SOUND, _basicFunc)(*args, **kwargs)

def playMusic(*args, **kwargs):
    return _funcs.get(FUNC_PLAY_MUSIC, _basicFunc)(*args, **kwargs)

def stopSounds(*args, **kwargs):
    return _funcs.get(FUNC_STOP_SOUNDS, _basicFunc)(*args, **kwargs)

def stopMusic(*args, **kwargs):
    return _funcs.get(FUNC_STOP_MUSIC, _basicFunc)(*args, **kwargs)

def setSoundVolume(*args, **kwargs):
    return _funcs.get(FUNC_SET_SOUND_VOLUME, _basicFunc)(*args, **kwargs)

def setMusicVolume(*args, **kwargs):
    return _funcs.get(FUNC_SET_MUSIC_VOLUME, _basicFunc)(*args, **kwargs)

def getSoundVolume(*args, **kwargs):
    return _funcs.get(FUNC_GET_SOUND_VOLUME, _basicFunc)(*args, **kwargs)

def getMusicVolume(*args, **kwargs):
    return _funcs.get(FUNC_GET_MUSIC_VOLUME, _basicFunc)(*args, **kwargs)

def toggleSound(*args, **kwargs):
    return _funcs.get(FUNC_TOGGLE_SOUND, _basicFunc)(*args, **kwargs)

def toggleMusic(*args, **kwargs):
    return _funcs.get(FUNC_TOGGLE_MUSIC, _basicFunc)(*args, **kwargs)

def playWithIntro(*args, **kwargs):
    return _funcs.get(FUNC_PLAY_WITH_INTRO, _basicFunc)(*args, **kwargs)

def preloadMusic(*args, **kwargs):
    return _funcs.get(FUNC_PRELOAD_MUSIC, _basicFunc)(*args, **kwargs)

def preloadSound(*args, **kwargs):
    return _funcs.get(FUNC_PRELOAD_SOUND, _basicFunc)(*args, **kwargs)

def anySoundPlaying(*args, **kwargs):
    return _funcs.get(FUNC_ANY_SOUND_PLAYING, _basicFunc)(*args, **kwargs)


def initAudio():
    global playSound, playMusic, stopSounds, stopMusic, setSoundVolume, setMusicVolume, getSoundVolume, getMusicVolume
    global toggleSound, toggleMusic, playWithIntro, preloadMusic, preloadSound, anySoundPlaying
    try:
        from . import sfmlAudio
        sfmlAudio.initAudio()
        _funcs[FUNC_PLAY_SOUND] = sfmlAudio.playSound
        _funcs[FUNC_PLAY_MUSIC] = sfmlAudio.playMusic
        _funcs[FUNC_STOP_SOUNDS] = sfmlAudio.stopSounds
        _funcs[FUNC_STOP_MUSIC] = sfmlAudio.stopMusic
        _funcs[FUNC_SET_SOUND_VOLUME] = sfmlAudio.setSoundVolume
        _funcs[FUNC_GET_SOUND_VOLUME] = sfmlAudio.getSoundVolume
        _funcs[FUNC_SET_MUSIC_VOLUME] = sfmlAudio.setMusicVolume
        _funcs[FUNC_GET_MUSIC_VOLUME] = sfmlAudio.getMusicVolume
        _funcs[FUNC_TOGGLE_SOUND] = sfmlAudio.toggleSound
        _funcs[FUNC_TOGGLE_MUSIC] = sfmlAudio.toggleMusic
        _funcs[FUNC_PLAY_WITH_INTRO] = sfmlAudio.playWithIntro
        _funcs[FUNC_PRELOAD_MUSIC] = sfmlAudio.preloadMusic
        _funcs[FUNC_PRELOAD_SOUND] = sfmlAudio.preloadSound
        _funcs[FUNC_ANY_SOUND_PLAYING] = sfmlAudio.anySoundPlaying
    except Exception as e:
        debugMessage("Couldn't initialize sfml backend; falling back to pyglet")
        debugMessage(e)
        try:
            from . import pygletAudio
            pygletAudio.initAudio()
            _funcs[FUNC_PLAY_SOUND] = pygletAudio.playSound
            _funcs[FUNC_PLAY_MUSIC] = pygletAudio.playMusic
            _funcs[FUNC_STOP_SOUNDS] = pygletAudio.stopSounds
            _funcs[FUNC_STOP_MUSIC] = pygletAudio.stopMusic
            _funcs[FUNC_SET_SOUND_VOLUME] = pygletAudio.setSoundVolume
            _funcs[FUNC_GET_SOUND_VOLUME] = pygletAudio.getSoundVolume
            _funcs[FUNC_SET_MUSIC_VOLUME] = pygletAudio.setMusicVolume
            _funcs[FUNC_GET_MUSIC_VOLUME] = pygletAudio.getMusicVolume
            _funcs[FUNC_TOGGLE_SOUND] = pygletAudio.toggleSound
            _funcs[FUNC_TOGGLE_MUSIC] = pygletAudio.toggleMusic
            _funcs[FUNC_PLAY_WITH_INTRO] = pygletAudio.playWithIntro
            _funcs[FUNC_PRELOAD_MUSIC] = pygletAudio.preloadMusic
            _funcs[FUNC_PRELOAD_SOUND] = pygletAudio.preloadSound
            _funcs[FUNC_ANY_SOUND_PLAYING] = pygletAudio.anySoundPlaying
        except Exception as e2:
            debugMessage("WARNING: Couldn't initialize any audio backend; sound disabled")
            debugMessage(e2)
            
        
