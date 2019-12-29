

from kaiengine.debug import debugMessage

from .base import *
from .effects import *
from .fallback import *

def getShaderProgram(context):
    return context.program(vertex_shader=DEFAULT_VERTEX_SHADER, fragment_shader=DEFAULT_FRAGMENT_SHADER)
