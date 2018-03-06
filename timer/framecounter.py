

#main frame counter

class FrameCounter(object):
    def __init__(self):
        self.frames_passed = 0
        self._pause = False

    def tickCounter(self):
        if not self.checkPaused():
            self.frames_passed += 1
        return self.frames_passed

    def pauseCounter(self):
        self._pause = True

    def unpauseCounter(self):
        self._pause = False

    def checkCurrentFrame(self):
        return self.frames_passed

    def checkPaused(self):
        return self._pause

global_frame_counter = FrameCounter()
