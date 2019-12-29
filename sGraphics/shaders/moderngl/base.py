DEFAULT_VERTEX_SHADER='''
        #version 330

        in vec2 tex;
        in vec2 coord;
        in vec4 color;
        in mat4 userdata;
        uniform mat4 orthom;
        uniform float time;
        out vec2 texcoord;
        out vec4 colormod;
        void main() {
            texcoord = tex;
            colormod = color;
            vec2 clampedcoords = vec2(floor(coord.x+0.001), floor(coord.y+0.001));
            gl_Position = vec4(clampedcoords.x, clampedcoords.y, 0.0, 1.0) * orthom;
        }
    '''
DEFAULT_FRAGMENT_SHADER='''
        #version 330

        uniform sampler2D texture1;
        uniform float time;
        in vec2 texcoord;
        in vec4 colormod;

        void main() {
            gl_FragColor = texture2D(texture1, texcoord) * colormod;
        }
    '''
