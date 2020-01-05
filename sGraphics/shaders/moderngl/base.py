DEFAULT_VERTEX_SHADER='''
        #version 330

        in vec2 tex;
        in vec2 coord;
        in vec4 color;
        in mat4 userdata;
        uniform mat4 orthom;
        uniform float time;
        uniform float layer;
        uniform vec2 scaling;
        out vec2 texcoord;
        out vec4 colormod;
        out float dont_purge;
        void main() {
            texcoord = tex;
            colormod = color;
            dont_purge = layer * scaling.x;
            vec2 clampedcoords = vec2(floor(coord.x+0.001), floor(coord.y+0.001));
            gl_Position = vec4(clampedcoords.x, clampedcoords.y, 0.0, 1.0) * orthom;
        }
    '''
DEFAULT_FRAGMENT_SHADER='''
        #version 330

        uniform sampler2D texture1;
        uniform float time;
        uniform vec2 step;
        in vec2 texcoord;
        in vec4 colormod;
        in float dont_purge;

        void main() {
            float dont_purge_this_either = 1.0 + ((dont_purge * step.x * time) / 1000000000.0);
            gl_FragColor = texture2D(texture1, texcoord) * colormod * dont_purge_this_either;
        }
    '''
