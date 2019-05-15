

from kaiengine.fonts import getWidth
from kaiengine.localization import getLocaleUnitLengths, getLocaleUnit, getLocaleUnitTooBig

from math import floor, log
from numpy import array, linalg
from itertools import chain

#a simple mouse tracker
_mouse_x = 0
_mouse_y = 0

def setMousePosition(x, y, *args, **kwargs):
    global _mouse_x, _mouse_y
    _mouse_x = x
    _mouse_y = y
    
def getMousePosition():
    '''Returns the current mouse position'''
    return (_mouse_x, _mouse_y)

def getDistance(source, dest):
    a = array((source[0], source[1]))
    b = array((dest[0], dest[1]))
    return linalg.norm(a-b)

def getBugfixedText(text):
    '''Circumvents a stupid positioning bug with PIL.'''
    if len(text) == 0: return ""
    if text[-1] == "j" or text[-1] == "y":
        return text + " "
    return text

def wrapText(text, maxWidth, textSize, font):
    '''Returns text as a list of lines no longer than maxWidth when rendered in font.'''
    words = text.split()
    index = 0
    wordBreaks = [0]
    lines = []
    while index < len(words):
        while index < len(words) and getWidth(" ".join(words[wordBreaks[-1]:index]), textSize, font) < maxWidth:
            index += 1
        if index != len(words) or getWidth(" ".join(words[wordBreaks[-1]:index]), textSize, font) > maxWidth:
            wordBreaks.append(index-1)
    wordBreaks.append(len(words))
    for start, end in zip(wordBreaks, wordBreaks[1:]):
        lines.append(" ".join(words[start:end]))
    return lines

WRAPPING_STYLE_DEFAULT = "default"
WRAPPING_STYLE_SPACES = "wrap_spaces"
WRAPPING_STYLE_CJK = "wrap_cjk"
WRAPPING_FUNCTIONS = {WRAPPING_STYLE_DEFAULT:wrapText,
                        WRAPPING_STYLE_SPACES:wrapText,
                        WRAPPING_STYLE_CJK:wrapText} #TODO: actually implement Japanese wrap here


def truncNumbers(val, digitnum = 5, add_spaces = False, locale = None): # 5 digits default. Less than this is dangerous and can glitch with high numbers, especially with negatives
    val = int(val)
    try: digits = int(log(abs(val), 10)) + (2 if val < 0 else 1) #add additional digit for negative sign if appropriate
    except ValueError: #must be 0
        val = 0
    else:
        lengths_list = getLocaleUnitLengths(locale)
        if len(lengths_list) > 0:
            if digits - lengths_list[-1] + 2 > digitnum:
                val = getLocaleUnitTooBig(locale)
            elif digits > digitnum:
                for i, truncamount in enumerate(lengths_list):
                    if digits - truncamount + 2 <= digitnum:
                        val = str(int(val / (10 ** (truncamount - 1)))) + getLocaleUnit(i, locale)
                        break
    val = str(val)
    if add_spaces:
        val = " "*(digitnum - len(val)) + val
    return val


def dictUnion(*dicts): #later dictionaries will preferentially use their keys over early dictionaries
    return dict(chain.from_iterable(dictionary.items() for dictionary in dicts))
