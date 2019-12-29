# -*- coding: utf-8 -*-

from kaiengine.event import joybuttonPressEvent, joybuttonReleaseEvent

JOYSTICK_PREFIX = "JOY_"

joysticks = []

def _joyButtonPress(joystick, button):
    joybuttonPressEvent(joystick, JOYSTICK_PREFIX + str(button))

def _joyButtonRelease(joystick, button):
    joybuttonReleaseEvent(joystick, JOYSTICK_PREFIX + str(button))

def _joyAxisMotion(joystick, axis, value):
    if value > 0.01 or value < -0.01:
        joybuttonPressEvent(joystick, str(axis) + str((-1 if value < 0 else 1) * 1.0))
    else:
        joybuttonReleaseEvent(joystick, str(axis) + str(0))


def initJoysticks():
    joysticks.clear()
    #TODO: replace pyglet call (pyglet.input.get_joysticks)
    joysticks.extend(get_joysticks())
    for stick in joysticks:
        stick.on_joybutton_press = _joyButtonPress
        stick.on_joybutton_release = _joyButtonRelease
        stick.on_joyaxis_motion = _joyAxisMotion
        stick.open()
