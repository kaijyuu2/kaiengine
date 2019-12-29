

COMPAT_VERT_SHADER = '''#version 330
                attribute vec2 tex;
                attribute vec2 coord;
                attribute vec4 color;
                attribute mat4 userdata;
                uniform mat4 orthom;
                uniform float time;
                varying vec2 texcoord;
                varying vec4 colormod;
                void main() {
                    texcoord = tex;
                    colormod = color;
                    vec2 clampedcoords = vec2(floor(coord.x+0.001f), floor(coord.y+0.001f));
                    gl_Position = vec4(clampedcoords.x, clampedcoords.y, 0.0, 1.0) * orthom;
                }'''

COMPAT_SVERT_SHADER = '''#version 330
                attribute vec2 tex;
                attribute vec2 coord;
                uniform vec2 scaling;
                uniform float time;
                varying vec2 texcoord;
                void main() {
                    texcoord = vec2(((tex.x+1.0)/2.0)/scaling.x, ((tex.y+1.0)/2.0)/scaling.y);
                    gl_Position = vec4(coord.x, coord.y, 0.0, 1.0);
                }'''

COMPAT_FRAG_SHADER = """#version 330
    uniform sampler2D texture1;
    uniform float time;
    varying vec2 texcoord;
    varying vec4 colormod;

    void main() {
        gl_FragColor = texture2D(texture1, texcoord) * colormod;
    }"""

COMPAT_SFRAG_SHADER = """#version 330
    uniform sampler2D texture1;
    uniform float time;
    uniform vec2 step;
    varying vec2 texcoord;

    void main() {
        gl_FragColor = texture2D(texture1, texcoord);
    }"""

COMPAT_OVERTEX_SHADER = '''#version 330
                attribute vec2 tex;
                attribute vec2 coord;
                varying vec2 texcoord;
                void main() {
                    texcoord = tex;
                    gl_Position = vec4(coord.x, coord.y, 0.0, 1.0);
                }'''

COMPAT_OFRAG_SHADER = """#version 330
        uniform sampler2D texture1;
        varying vec2 texcoord;

        void main() {
            gl_FragColor = texture2D(texture1, texcoord);
        }"""
