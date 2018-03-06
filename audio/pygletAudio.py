
from kaiengine.debug import debugMessage


sounds = {}
music = None
media = None

volumes = {"sound":1.0, "music":1.0}

enabledChannels = {"sound":True, "music":True}

def initAudio():
    global music
    global media
    import pyglet
    pyglet.options['search_local_libs'] = True
    media = pyglet.media
    music = media.Player()
    

def _purgeSound(sound_path, player):
    try:
        player.delete()
        sounds[sound_path].remove(player)
    except:
        #don't care if it fails; probably already removed
        pass

def anySoundPlaying(sound_path):
    '''TODO: IMPLEMENT'''
    return False

def preloadSound(sound_path):
    '''TODO: IMPLEMENT'''
    pass

def preloadMusic(music_path):
    '''TODO: IMPLEMENT'''
    pass

def playSound(sound_path, cancel_others = False):
    if not enabledChannels["sound"]: return
    if sound_path is None: return
    try:
        sound = media.load(sound_path, streaming=False)
        if sound_path not in sounds:
            sounds[sound_path] = []
        elif cancel_others:
            for other in sounds[sound_path]:
                other.pause()
            sounds[sound_path] = []
        player = media.Player()
        player.volume = getSoundVolume()
        player.queue(sound)
        player.play()
        player.on_eos = lambda: _purgeSound(sound_path, player)
        sounds[sound_path].append(player)
    except Exception as e:
        debugMessage(e)
        debugMessage("Audio playback error.")

def playMusic(musicPath, loop = True, fadeOut = None):
    if musicPath is None: return
    global music
    music.pause()
    music = media.Player()
    _updateMusicVolume()
    try:
        track = media.load(musicPath)
        track.loop = loop
        music.queue(track)
        music.play()
    except Exception as e:
        debugMessage(e)
        debugMessage("Audio playback error.")

def playWithIntro(introMusicPath, loopingMusicPath):
    class DelayedLoopPlayer(media.Player):
        def next_source(self):
            super().next_source()
            self.loop = True
    if introMusicPath is None or loopingMusicPath is None: return
    global music
    music.pause()
    music = DelayedLoopPlayer()
    _updateMusicVolume()
    try:
        intro = media.load(introMusicPath, streaming=False)
        loopingTrack = media.load(loopingMusicPath, streaming=False)
        #looping = media.SourceGroup(loopingTrack.audio_format, None)
        #looping.loop = True
        #looping.queue(loopingTrack)
        music.queue(intro)
        music.queue(loopingTrack)
        music.play()
    except Exception as e:
        debugMessage(e)
        debugMessage("Audio playback error.")

def stopSounds():
    for soundPath, soundSet in list(sounds.items()):
        for soundplayer in soundSet:
            soundplayer.pause()
            soundplayer.delete()
    sounds.clear()

def stopMusic(fade=None):
    global music
    music.pause()
    music = media.Player()
    _updateMusicVolume()

def setSoundVolume(newVolume):
    volumes["sound"] = newVolume
    for soundPath, soundSet in list(sounds.items()):
        for soundplayer in soundSet:
            soundplayer.volume = newVolume

def setMusicVolume(newVolume):
    volumes["music"] = newVolume
    music.volume = getMusicVolume()
    _updateMusicVolume()

def getSoundVolume():
    return volumes["sound"]

def getMusicVolume():
    return volumes["music"]

def _updateMusicVolume():
    if not enabledChannels["music"]:
        music.volume = 0
    else:
        music.volume = getMusicVolume()

def _soundOff():
    enabledChannels["sound"] = False

def _musicOff():
    enabledChannels["music"] = False

def _soundOn():
    enabledChannels["sound"] = True

def _musicOn():
    enabledChannels["music"] = True

def toggleSound(val = None):
    if val is False or (val is None and enabledChannels["sound"]):
        _soundOff()
    else:
        _soundOn()

def toggleMusic(val = None):
    if val is False or (val is None and enabledChannels["music"]):
        _musicOff()
    else:
        _musicOn()
    _updateMusicVolume()
