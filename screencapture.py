

from . import sGraphics
from .timer import schedule, unschedule
from kaiengine.debug import debugMessage

import os

# screenshot data

screenshot_data = []



def takeScreenshot(*args, **kwargs):
    """Capture and return a PIL image of the current screen."""
    #TODO: check everything is initialized and OK
    #TODO: handle sGraphics.InvalidScreenshotCoordinatesError here?
    screenshot = sGraphics.takeScreenshot(*args, **kwargs)
    return screenshot

def dumpScreenshot(screenshotPath=None, screenshotDir=None):
    """Take a screenshot and save it to a specified or default path."""
    originalDir = os.getcwd()
    try:
        screenshot = takeScreenshot()
        if screenshotDir is not None:
            os.chdir(screenshotDir)
        if screenshotPath is None:
            index = 1
            while os.path.exists("screenshot%05i.png" % index):
                index += 1
            screenshotPath = "screenshot%05i.png" % index
        try:
            screenshot.save(screenshotPath)
        except IOError as e:
            debugMessage("Screenshot I/O error({0}): {1}".format(e.errno, e.strerror))
    finally:
        os.chdir(originalDir)

def startAnimationCapture(hardDiskCache=False):
    """Begin capturing every graphical frame to create an animation."""
    #hardDiskCache NYI due to various concerns
    if not hardDiskCache:
        finishAnimationCapture() #stop any current capture
        schedule(_captureAnimation, 1, True)
        _captureAnimation() #do it this frame too

def _captureAnimation():
    screenshot_data.append(takeScreenshot(palette=True))

def captureInProgress():
    """Return True if an animation is being captured."""
    return len(screenshot_data) > 0

def finishAnimationCapture(savePath=None):
    """Complete animation capture and save frames to disk."""
    global screenshot_data
    unschedule(_captureAnimation) #unschedule if needed
    if not screenshot_data: #check if we don't have any available capture data
        return

    if savePath is None:
        index = 1
        while os.path.exists("animation%05i.gif" % index):
            index += 1
        savePath = "animation%05i.gif" % index

    try:
        screenshot_data[0].save(savePath,
                                save_all=True,
                                append_images=screenshot_data[1:],
                                loop=0,
                                duration=25)
    except IOError as e:
        debugMessage("Animation I/O error({0}): {1}".format(e.errno, e.strerror))

    screenshot_data = []

def toggleAnimationCapture(savePath=None, hardDiskCache=False):
    if captureInProgress():
        finishAnimationCapture(savePath)
    else:
        startAnimationCapture(hardDiskCache)
