# -*- coding: utf-8 -*-

import asyncio
import concurrent
import numpy
import sounddevice
import soundfile

from kaiengine.debug import debugMessage
from kaiengine.resource import loadResource, ResourceUnavailableError
from kaiengine.timer import getGameScheduler, scheduleRealtime

_currently_playing = []
AUDIO_GARBAGE_COLLECTION_INTERVAL = 10

def _garbage_collect(*args):
    global _currently_playing
    _currently_playing = [task for task in _currently_playing if not task.done()]

def initAudio():
    scheduleRealtime(_garbage_collect, AUDIO_GARBAGE_COLLECTION_INTERVAL, repeat=True)

async def _play_data(data, event_loop, *, loop, start, end, loop_start, fade_in, fade_out, crossfade, start_paused):
    length = end or len(data)
    event = asyncio.Event()
    index = start

    if loop:
        def callback(outdata, frame_count, time_info, status):
            nonlocal index
            remainder = length - index
            valid_frames = min(frame_count, remainder)
            outdata[:valid_frames] = data[index:index+valid_frames]
            if frame_count > remainder:
                index = loop_start
                overshoot = frame_count - remainder
                outdata[valid_frames:valid_frames+overshoot] = data[index:index+overshoot]
                outdata[valid_frames+overshoot:] = 0
                index += overshoot
            else:
                outdata[valid_frames:] = 0
                index += valid_frames
    else:
        def callback(outdata, frame_count, time_info, status):
            nonlocal index
            remainder = length - index
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
        await asyncio.sleep(1)

def _load_from_file(file_handle):
    data, sample_rate = soundfile.read(file_handle, dtype='float32')
    return (data, sample_rate)

async def _play_from_file(file_handle, event_loop, thread_loading = True, **kwargs):
    if thread_loading:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            data, sample_rate = await event_loop.run_in_executor(pool, _load_from_file, file_handle)
    else:
        data, sample_rate = soundfile.read(file_handle, dtype='float32')
    await _play_data(data, event_loop, **kwargs)

def playAudio(file_path = None, channel = "special", thread_loading = True, loop = False, start = 0, end = None, loop_start = 0, fade_in = None, fade_out = None, crossfade = None, start_paused = False):
    try:
        file_handle = loadResource(file_path)
    except ResourceUnavailableError as e:
        debugMessage(e)
        debugMessage("Couldn't load resource: " + file_path)
    else:
        event_loop = getGameScheduler()
        _currently_playing.append(asyncio.create_task(_play_from_file(file_handle, event_loop, thread_loading=thread_loading, loop=loop,
                                                                      start=start, end=end, loop_start=loop_start,
                                                                      fade_in=fade_in, fade_out=fade_out,
                                                                      crossfade=crossfade, start_paused=start_paused)))

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
