

from kaiengine.timer import scheduleRealtime, unscheduleRealtime
from kaiengine.resource import loadResource

#constants
VOLUME_MULTIPLIER = 100.0

#dict keys
SOUND_BUFFER = "sound_buffer"
SOUND_OBJECTS = "sound_objects"

#sfml module
audio = None

#global variables

currently_playing_effects = {}
currently_playing_music = []
currently_playing_theme = []
sound_memory = {}
music_buffers = {}
music_memory = {}
buffers = {}

sound_volume = VOLUME_MULTIPLIER
music_volume = VOLUME_MULTIPLIER
music_enabled = True
sound_enabled = True

loop_interrupted = [False]

unschedule_list = []

def initAudio():
    global audio
    from sfml import audio as sfmlaudio
    audio = sfmlaudio

def toggleMusic(val = None):
    global music_enabled
    if val is None:
        val = not music_enabled
    music_enabled = val
    setMusicVolume(float(music_volume)/VOLUME_MULTIPLIER)

def toggleSound(val = None):
    global sound_enabled
    if val is None:
        val = not sound_enabled
    sound_enabled = val
    setSoundVolume(float(sound_volume)/VOLUME_MULTIPLIER)

def playSound(sound_path, cancel_others = False):
    '''Play a sound effect file once.'''
    if not sound_enabled: return
    if sound_path is None: return
    try:
        buff = currently_playing_effects[sound_path][SOUND_BUFFER]
        if cancel_others:
            for sound in currently_playing_effects[sound_path][SOUND_OBJECTS]:
                sound.stop()
    except KeyError:
        currently_playing_effects[sound_path] = {}
        if sound_path not in sound_memory:
            sound_memory[sound_path] = loadResource(sound_path).getvalue()
        buff = audio.SoundBuffer.from_memory(sound_memory[sound_path])
        currently_playing_effects[sound_path][SOUND_BUFFER] = buff
        currently_playing_effects[sound_path][SOUND_OBJECTS] = []
    effect = audio.Sound()
    effect.buffer = buff
    if sound_enabled:
        effect.volume = sound_volume
    else:
        effect.volume = 0
    effect.play()
    currently_playing_effects[sound_path][SOUND_OBJECTS].append(effect)
    _purgeFinishedSounds()
    return effect

def anySoundPlaying(sound_path):
    _purgeFinishedSounds()
    return sound_path in currently_playing_effects

def _soundFinished(sound):
    return sound.status == audio.Status.STOPPED

def stopMusic(fade=None):
    '''Stop all currently playing music.'''
    global currently_playing_music
    global currently_playing_theme
    for handle in unschedule_list:
        unscheduleRealtime(handle)
    for music in currently_playing_music:
        music.stop()
    for music in currently_playing_theme:
        music.stop()
    currently_playing_music = []
    currently_playing_theme = []

def stopSounds():
    '''Stop all currently playing sounds.'''
    for key, data in list(currently_playing_effects.items()):
        for sound in data[SOUND_OBJECTS]:
            sound.stop()
    _purgeFinishedSounds()

def preloadMusic(music_path):
    '''Preload a song.'''
    if music_path not in music_memory:
        music_memory[music_path] = loadResource(music_path).getvalue()
    if music_path not in music_buffers:
        music_buffers[music_path] = audio.SoundBuffer.from_memory(music_memory[music_path])

def preloadSound(sound_path):
    '''Preloads a sound effect.'''
    if sound_path not in sound_memory:
        sound_memory[sound_path] = loadResource(sound_path).getvalue()

def playMusic(musicPath, loop=True, fadeOut=None):
    '''Play a music file.'''
    loop_interrupted[0] = True
    global currently_playing_music
    for music in currently_playing_music:
        music.stop()
    currently_playing_music = []
    if musicPath is None: return
    if musicPath not in music_memory:
        music_memory[musicPath] = loadResource(musicPath).getvalue()
    if musicPath not in music_buffers:
        music_buffers[musicPath] = audio.SoundBuffer.from_memory(music_memory[musicPath])
    music = audio.Sound(music_buffers[musicPath])
    music.loop = loop
    if music_enabled:
        music.volume = int(music_volume)
    else:
        music.volume = 0
    if len(currently_playing_theme) == 0:
        music.play()
    currently_playing_music.append(music)
    return music

def setSoundVolume(newVolume):
    '''Adjusts the volume of all sound effects from 0 (mute) to 1.0 (maximum).'''
    global sound_volume
    sound_volume = VOLUME_MULTIPLIER*newVolume
    if sound_enabled:
        volume = sound_volume
    else:
        volume = 0
    for data in list(currently_playing_effects.values()):
        for effect in data[SOUND_OBJECTS]:
            effect.volume = int(volume)

def getSoundVolume():
    return sound_volume/VOLUME_MULTIPLIER

def setMusicVolume(newVolume):
    '''Adjusts the volume of all music from 0 (mute) to 1.0 (maximum).'''
    global music_volume
    music_volume = VOLUME_MULTIPLIER*newVolume
    if music_enabled:
        volume = music_volume
    else:
        volume = 0
    for music in currently_playing_theme:
        music.volume = volume
    for music in currently_playing_music:
        music.volume = volume

def getMusicVolume():
    return music_volume/VOLUME_MULTIPLIER

def _purgeFinishedSounds(useless_arg = None):
    '''Call every once in a while to clean up old sound effects.'''
    for key, data in list(currently_playing_effects.items()):
        data[SOUND_OBJECTS] = [sound for sound in data[SOUND_OBJECTS] if not _soundFinished(sound)]
        if len(data[SOUND_OBJECTS]) <= 0:
            del currently_playing_effects[key]
        
def _playLoopingSection(STUPIDPYGLET, musicPath):
    if not loop_interrupted[0]:
        playMusic(musicPath)

def playWithIntro(introMusicPath, loopingMusicPath):
    """Play a song that has a one-time intro section, then a looping section."""
    while len(unschedule_list) > 0:
        unscheduleRealtime(unschedule_list.pop())
    intro = playMusic(introMusicPath, loop=False)
    loop_interrupted[0] = False
    preloadMusic(loopingMusicPath)
    unschedule_list.append(scheduleRealtime(_playLoopingSection, music_buffers[introMusicPath].duration.seconds, False, loopingMusicPath))

scheduleRealtime(_purgeFinishedSounds, 10.0, True) #automagically purge every 10 seconds
