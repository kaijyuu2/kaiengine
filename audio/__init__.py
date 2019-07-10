

"""Public API:

    NOTE: For convenience, functions have aliases with "Sound" or "Music" in place of "Audio" which set the value of channel to "sound" or "music".
    NOTE: Channel of None makes the function affect all channels.

playAudio(file_path, channel = "special", loop = False, start = None, end = None, loop_start = None, fade_in = None, fade_out = None, crossfade = None)

    Play an audio file from file_path on channel, fading in volume over fade_in seconds.
    Starts from start seconds (or the beginning of the file) and ends at end seconds (or the end of the file).
    If looping, playback smoothly continues from loop_start, or start, or the beginning of the file.
    If not looping, fades out volume over the last fade_out seconds of playback before the end.
    Playing a sound on the "music" channel stops the current music, if any. The old and new tracks crossfade over crossfade seconds.

anyAudioPlaying(file_path, channel = None)

    Check if any audio derived from file_path is currently playing on channel.

pauseAudio(channel = None)

    Stops playback on channel, but remembers the current playback position.

resumeAudio(channel = None)

    Resumes playback of paused audio on channel.

stopAudio(channel = None, fade_out = None)

    Stops all playback on channel, fading out over fade_out seconds.

stopAudioFile(file_path, channel = None, fade_out = None)

    Stops playback of any audio derived from file_path on channel, fading out over fade_out seconds.

setAudioVolume(channel = None, new_volume = 0.5)

    Set volume of audio on a channel from 0.0 (mute) to 1.0 (maximum).
    If channel is None, set master volume instead.
    Channel volumes are multiplicative with master volume.

getAudioVolume(channel = None)

    Return current channel volume from 0.0 (mute) to 1.0 (maximum).
    If channel is None, return master volume instead.

disableAudio(channel = None)

    Stop playing audio on channel immediately.
    Play commands for disabled channels will be silently ignored.

enableAudio(channel = None)

    Make channel not be disabled.

toggleAudio(channel = None, enable = True)

    Call disableAudio or enableAudio for channel, depending on enable.


"""

from .functions import *
