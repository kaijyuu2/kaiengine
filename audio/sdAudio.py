# -*- coding: utf-8 -*-

import numpy
import sounddevice
import soundfile


def initAudio():
    return None


def playAudio(*args, **kwargs):
    return None

def anyAudioPlaying(*args, **kwargs):
    return None

def pauseAudio(*args, **kwargs):
    return None

def resumeAudio(*args, **kwargs):
    return None

def stopAudio(*args, **kwargs):
    return None

def stopAudioFile(*args, **kwargs):
    return None

def setAudioVolume(*args, **kwargs):
    return None

def getAudioVolume(*args, **kwargs):
    return None

def disableAudio(*args, **kwargs):
    return None

def enableAudio(*args, **kwargs):
    return None

def toggleAudio(*args, **kwargs):
    return None




def playSound(*args, **kwargs):
    return playAudio(*args, channel="sound", **kwargs)

def anySoundPlaying(*args, **kwargs):
    return anyAudioPlaying(*args, channel="sound", **kwargs)

def pauseSound(*args, **kwargs):
    return pauseAudio(*args, channel="sound", **kwargs)

def resumeSound(*args, **kwargs):
    return resumeAudio(*args, channel="sound", **kwargs)

def stopSound(*args, **kwargs):
    return stopAudio(*args, channel="sound", **kwargs)

def stopSoundFile(*args, **kwargs):
    return stopAudioFile(*args, channel="sound", **kwargs)

def setSoundVolume(*args, **kwargs):
    return setAudioVolume(*args, channel="sound", **kwargs)

def getSoundVolume(*args, **kwargs):
    return getAudioVolume(*args, channel="sound", **kwargs)

def disableSound(*args, **kwargs):
    return disableAudio(*args, channel="sound", **kwargs)

def enableSound(*args, **kwargs):
    return enableAudio(*args, channel="sound", **kwargs)

def toggleSound(*args, **kwargs):
    return toggleAudio(*args, channel="sound", **kwargs)

def playMusic(*args, **kwargs):
    return playAudio(*args, channel="music", **kwargs)

def anyMusicPlaying(*args, **kwargs):
    return anyAudioPlaying(*args, channel="music", **kwargs)

def pauseMusic(*args, **kwargs):
    return pauseAudio(*args, channel="music", **kwargs)

def resumeMusic(*args, **kwargs):
    return resumeAudio(*args, channel="music", **kwargs)

def stopMusic(*args, **kwargs):
    return stopAudio(*args, channel="music", **kwargs)

def stopMusicFile(*args, **kwargs):
    return stopAudioFile(*args, channel="music", **kwargs)

def setMusicVolume(*args, **kwargs):
    return setAudioVolume(*args, channel="music", **kwargs)

def getMusicVolume(*args, **kwargs):
    return getAudioVolume(*args, channel="music", **kwargs)

def disableMusic(*args, **kwargs):
    return disableAudio(*args, channel="music", **kwargs)

def enableMusic(*args, **kwargs):
    return enableAudio(*args, channel="music", **kwargs)

def toggleMusic(*args, **kwargs):
    return toggleAudio(*args, channel="music", **kwargs)
