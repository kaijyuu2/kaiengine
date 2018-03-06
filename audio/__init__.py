

"""Public API:

playSound(sound_path, cancel_others = False)

    Play an audio file once.
    Does not affect music.
    Stop other sounds with the same path if cancel_others is True.

playMusic(musicPath, loop = True, fadeOut = None)

    Play an audio file.
    Loops unless loop is False.
    If fadeOut is None or not supported, stops other music immediately.
    (See stopMusic for more on fade support.)

playWithIntro(introMusicPath, loopingMusicPath)

    Play a one-time intro audio file, then a looping section as music.

anySoundPlaying(sound_path)

    Check if any sound derived from south_path is currently playing.

stopSounds()

    Immediately stop all currently playing sound effects.

stopMusic(fade = None)

    Stop playing the current music, if any.
    Fade may not be supported on some backends.
    If fade is None or not supported, music will stop instantly.
    If fade is supported, music will fade out over that many seconds.

preloadSound(sound_path)
preloadMusic(music_path)

    Preemptively loads audio file data to reduce seek times.
    Data is not decoded, so it is safe to call on numerous songs.

setSoundVolume(newVolume)
setMusicVolume(newVolume)

    Adjust volume of audio on a channel from 0.0 (mute) to 1.0 (maximum).

getSoundVolume()
getMusicVolume()

    Return current channel volume from 0.0 (mute) to 1.0 (maximum).

toggleSound(val = None)
toggleMusic(val = None)

    Toggle whether the channel plays at all.
    If val is True or False, set playback on or off.
    If val is None (default), toggle to opposite of current state.
    Music will reliably be playing in its expected state if toggled on.
    Sound will not play at all if played when in the off state.

"""

from .functions import *
