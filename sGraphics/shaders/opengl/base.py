

FRAG_SHADER_TEMPLATE = """#version 130
    uniform sampler2D texture1;
    uniform float time;
    in vec2 texcoord;
    in vec4 colormod;

    {0}

    void main() {{
        vec4 color = texture2D(texture1, texcoord) * colormod;
        {1};
        gl_FragColor = color;
    }}"""

POST_FRAG_SHADER_TEMPLATE = """#version 130
    uniform sampler2D texture1;
    uniform float time;
    uniform vec2 step;
    in vec2 texcoord;

    float rand(vec2 co) {{
            return fract(sin(dot(co.xy,vec2(12.9898,78.233))) * 43758.5453);
            }}

    {0}

    void main() {{
        vec4 color = texture2D(texture1, texcoord);
        {1};
        gl_FragColor = color;
    }}"""

BASE_VERTEX_SHADER = '''#version 130
                attribute vec2 tex;
                attribute vec2 coord;
                attribute vec4 color;
                attribute mat4 userdata;
                uniform mat4 orthom;
                uniform float time;
                out vec2 texcoord;
                out vec4 colormod;
                void main() {
                    texcoord = tex;
                    colormod = color;
                    vec2 clampedcoords = vec2(floor(coord.x+0.001f), floor(coord.y+0.001f));
                    gl_Position = vec4(clampedcoords.x, clampedcoords.y, 0.0, 1.0) * orthom;
                }'''

BASE_SVERTEX_SHADER = '''#version 130
                attribute vec2 tex;
                attribute vec2 coord;
                uniform vec2 scaling;
                uniform float time;
                out vec2 texcoord;
                void main() {
                    texcoord = vec2(((tex.x+1.0)/2.0)/scaling.x, ((tex.y+1.0)/2.0)/scaling.y);
                    gl_Position = vec4(coord.x, coord.y, 0.0, 1.0);
                }'''

BASE_FRAG_SHADER = """#version 130
    uniform sampler2D texture1;
    uniform float time;
    in vec2 texcoord;
    in vec4 colormod;

    void main() {
        gl_FragColor = texture2D(texture1, texcoord) * colormod;
    }"""

BASE_SFRAG_SHADER = """#version 130
    uniform sampler2D texture1;
    uniform float time;
    uniform vec2 step;
    in vec2 texcoord;

    void main() {
        gl_FragColor = texture2D(texture1, texcoord);
    }"""

OVERTEX_SHADER = '''#version 130
                attribute vec2 tex;
                attribute vec2 coord;
                out vec2 texcoord;
                void main() {
                    texcoord = tex;
                    gl_Position = vec4(coord.x, coord.y, 0.0, 1.0);
                }'''

OFRAG_SHADER = """#version 130
        uniform sampler2D texture1;
        in vec2 texcoord;

        void main() {
            gl_FragColor = texture2D(texture1, texcoord);
        }"""
