# -*- coding: utf-8 -*-

import asyncio
import concurrent
import numpy
import sounddevice
import soundfile

from kaiengine.resource import loadResource, ResourceUnavailableError
from kaiengine.timer import getGameScheduler, scheduleRealtime

_currently_playing = []
AUDIO_GARBAGE_COLLECTION_INTERVAL = 10

def _garbage_collect(*args):
    global _currently_playing
    _currently_playing = [task for task in _currently_playing if not task.done()]

def initAudio():
    scheduleRealtime(_garbage_collect, AUDIO_GARBAGE_COLLECTION_INTERVAL, repeat=True)

async def _play_data(data, event_loop):
    event = asyncio.Event()
    index = 0

    def callback(outdata, frame_count, time_info, status):
        nonlocal index
        remainder = len(data) - index
        if remainder == 0:
            event_loop.call_soon_threadsafe(event.set)
            raise sounddevice.CallbackStop
        valid_frames = min(frame_count, remainder)
        outdata[:valid_frames] = data[index:index+valid_frames]
        outdata[valid_frames:] = 0
        index += valid_frames

    stream = sounddevice.OutputStream(callback=callback, dtype=data.dtype, channels=data.shape[1])
    with stream:
        await event.wait()

def _load_from_file(file_handle):
    data, sample_rate = soundfile.read(file_handle, dtype='float32')
    return (data, sample_rate)

async def _play_from_file(file_handle, event_loop):
    with concurrent.futures.ThreadPoolExecutor() as pool:
        data, sample_rate = await event_loop.run_in_executor(pool, _load_from_file, file_handle)
    await _play_data(data, event_loop)

def playAudio(file_path, channel = "special", loop = False, start = None, end = None, loop_start = None, fade_in = None, fade_out = None, crossfade = None, start_paused = False):
    try:
        file_handle = loadResource(file_path)
    except ResourceUnavailableError as e:
        debugMessage(e)
        debugMessage("Couldn't load resource: " + file_path)
    else:
        event_loop = getGameScheduler()
        _currently_playing.append(asyncio.create_task(_play_from_file(file_handle, event_loop)))

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
