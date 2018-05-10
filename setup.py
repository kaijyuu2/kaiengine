

#quick setup functions


from . import display, fonts, camera, settings, resource, keybinds, simplefpscounter, audio, savegame, localization, event, joysticks, scene

from .gconfig import *

def setupWindowBasic(*logos):
    '''quick way to set up the window. pass one or more logo filenames'''
    display.setupWindow()
    display.setWindowLogo(*logos)
    display.setGlobalScaling(settings.getValue(DYNAMIC_SETTINGS_GLOBAL_SCALING))

def setupDrivers():
    resource.setupArchive()
    fonts.initializeFontDriver()
    localization.initLocalizationData()
    camera.initCamera()
    savegame.Initialize()
    keybinds.addBoundKeyDict(settings.getValue(DYNAMIC_SETTINGS_KEY_BINDS))
    joysticks.initJoysticks()
    audio.initAudio()
    audio.setMusicVolume(settings.getValue(DYNAMIC_SETTINGS_MUSIC_VOLUME))
    audio.setSoundVolume(settings.getValue(DYNAMIC_SETTINGS_SOUND_VOLUME))
    audio.toggleMusic(settings.getValue(DYNAMIC_SETTINGS_MUSIC_ON))
    audio.toggleSound(settings.getValue(DYNAMIC_SETTINGS_SOUND_ON))
    try:
        simplefpscounter.initializeSimpleFPSCounter()
    except resource.ResourceUnavailableError:
        pass
    scene.initializeSceneManager()
    event.initializeGlue()
    
def setupDriversMinimal():
    '''Sets only the minimal amount of drivers up (no audiovisual ones)'''
    resource.setupArchive()
    localization.initLocalizationData()
    event.initializeGlue()

def closeDrivers():
    simplefpscounter.removeFPS()
