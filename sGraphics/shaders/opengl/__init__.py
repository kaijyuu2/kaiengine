

from OpenGL.GL import shaders
from kaiengine.debug import debugMessage
from kaiengine.sGraphics.constants.opengl import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER

from kaiengine.sGraphics.shaders.opengl.base import *
from kaiengine.sGraphics.shaders.opengl.effects import *
from kaiengine.sGraphics.shaders.opengl.fallback import *

SHADERS_AVAILABLE = True

try:
    base_vertex_shader = shaders.compileShader(BASE_VERTEX_SHADER, GL_VERTEX_SHADER)
    base_screen_vertex_shader = shaders.compileShader(BASE_SVERTEX_SHADER, GL_VERTEX_SHADER)
    overlay_vert = shaders.compileShader(OVERTEX_SHADER, GL_VERTEX_SHADER)

    base_fragment_shader = shaders.compileShader(BASE_FRAG_SHADER, GL_FRAGMENT_SHADER)
    base_post_shader = shaders.compileShader(BASE_SFRAG_SHADER, GL_FRAGMENT_SHADER)
    overlay_frag = shaders.compileShader(OFRAG_SHADER, GL_FRAGMENT_SHADER)
except RuntimeError:
    debugMessage("WARNING: OpenGL 3.0 not supported; trying fallback shaders")
    SHADERS_AVAILABLE = False

    base_vertex_shader = shaders.compileShader(COMPAT_VERT_SHADER, GL_VERTEX_SHADER)
    base_screen_vertex_shader = shaders.compileShader(COMPAT_SVERT_SHADER, GL_VERTEX_SHADER)
    overlay_vert = shaders.compileShader(COMPAT_OVERTEX_SHADER, GL_VERTEX_SHADER)

    base_fragment_shader = shaders.compileShader(COMPAT_FRAG_SHADER, GL_FRAGMENT_SHADER)
    base_post_shader = shaders.compileShader(COMPAT_SFRAG_SHADER, GL_FRAGMENT_SHADER)
    overlay_frag = shaders.compileShader(COMPAT_OFRAG_SHADER, GL_FRAGMENT_SHADER)

DEFAULT_SHADER = shaders.compileProgram(base_vertex_shader, base_fragment_shader)
DEFAULT_SCREEN_SHADER = shaders.compileProgram(base_screen_vertex_shader, base_post_shader)
OVERLAY_SHADER = shaders.compileProgram(overlay_vert, overlay_frag)

SHADERS = {"default":DEFAULT_SHADER}
SCREEN_SHADERS = {"default":DEFAULT_SCREEN_SHADER}

CURRENT_SHADER = "default"
CURRENT_SCREEN_SHADER = "default"

def getShader():
    return SHADERS[CURRENT_SHADER]

def getScreenShader():
    return SCREEN_SHADERS[CURRENT_SCREEN_SHADER]

def _compVert(vertex_shader_data, default=base_vertex_shader):
    if vertex_shader_data:
        return shaders.compileShader(vertex_shader_data, GL_VERTEX_SHADER)
    return default

def _genShader(vertex_shader, fragment_shaders, fragment_template):
    _frag = fragment_template.format("\n\n".join([shader[0] for shader in fragment_shaders]),
                                       "\n".join([shader[1] for shader in fragment_shaders]))
    frag = shaders.compileShader(_frag, GL_FRAGMENT_SHADER)
    return shaders.compileProgram(vertex_shader, frag)

def _createSpriteShader(vertex_shader = None, fragment_shaders = [], handle="default"):
    if not SHADERS_AVAILABLE: return
    global CURRENT_SHADER
    CURRENT_SHADER = handle
    SHADERS[handle] = _genShader(_compVert(vertex_shader, base_vertex_shader),
                                        fragment_shaders,
                                        FRAG_SHADER_TEMPLATE)

def _createScreenShader(vertex_shader = None, fragment_shaders = [], handle="default"):
    if not SHADERS_AVAILABLE: return
    global CURRENT_SCREEN_SHADER
    CURRENT_SCREEN_SHADER = handle
    SCREEN_SHADERS[handle] = _genShader(_compVert(vertex_shader, base_screen_vertex_shader),
                                        fragment_shaders,
                                        POST_FRAG_SHADER_TEMPLATE)

def _swapSpriteShader(handle="default"):
    if not SHADERS_AVAILABLE: return
    global CURRENT_SHADER
    CURRENT_SHADER = handle

def _swapScreenShader(handle="default"):
    if not SHADERS_AVAILABLE: return
    global CURRENT_SCREEN_SHADER
    CURRENT_SCREEN_SHADER = handle
