

FRAG_SHADER_TEMPLATE = """#version 450
    precision highp float;
    uniform sampler2D texture1;
    uniform float time;
    varying vec2 texcoord;
    varying vec4 colormod;

    {0}

    void main() {{
        vec4 color = texture2D(texture1, texcoord) * colormod;
        {1};
        gl_FragColor = color;
    }}"""

POST_FRAG_SHADER_TEMPLATE = """#version 450
    precision highp float;
    uniform sampler2D texture1;
    uniform float time;
    uniform vec2 step;
    varying vec2 texcoord;

    float rand(vec2 co) {{
            return fract(sin(dot(co.xy,vec2(12.9898,78.233))) * 43758.5453);
            }}

    {0}

    void main() {{
        vec4 color = texture2D(texture1, texcoord);
        {1};
        gl_FragColor = color;
    }}"""

BASE_VERTEX_SHADER = '''#version 450
                void main() { gl_Position = gl_Vertex; }'''

BASE_SVERTEX_SHADER = '''#version 450
                void main() { gl_Position = gl_Vertex; }'''

BASE_FRAG_SHADER = """#version 450
    precision highp float;
    void main() { gl_FragColor = vec4(1,1,0,1); }"""

BASE_SFRAG_SHADER = """#version 450
    precision highp float;
    void main() { gl_FragColor = vec4(1,1,0,1); }"""

OVERTEX_SHADER = '''#version 450
                void main() { gl_Position = gl_Vertex; }'''

OFRAG_SHADER = """#version 450
        precision highp float;
    void main() { gl_FragColor = vec4(1,1,0,1); }"""
