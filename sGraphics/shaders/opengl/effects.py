

GBA_SHADER = ("""
vec4 gbashade(vec4 color) {
    vec4 basecolor = color;
    vec4 brightmod = pow(basecolor, vec4(2.7,2.7,2.7,2.7));
    brightmod = mix(brightmod, vec4(0.5,0.5,0.5,0.5), 0);
    mat4 colmo = mat4(vec4(0.81, 0.23, -0.04, 0.0),
                  vec4(0.09, 0.67,  0.24, 0.0),
                  vec4(0.15, 0.12,  0.73, 0.0),
                  vec4(0.0,  0.0,   0.0,  1.0));
    brightmod = mul(colmo, brightmod);
    return pow(brightmod, vec4(0.45454545, 0.45454545, 0.45454545, 0.45454545));}""",
    """color = gbashade(color);""")


VCR_DISTORTION_SHADER = ("""
vec4 vcrshade(vec4 color) {
    vec4 basecolor = color;
    if(rand(vec2(time, tan(texcoord.x)*cos(texcoord.y))) > 0.80){
    basecolor *= 0.875;
    for(int m=(-4);m<5;m++){
        for(int n=(-4);n<5;n++){
            basecolor += (texture2D(texture1, texcoord+(m*0.002, n*0.0037)) * 0.0025);
        };
    }};
    if(rand(vec2(time, tan(texcoord.y))) > 0.9){
    basecolor *= 0.875;
    for(int m=(-4);m<5;m++){
        for(int n=(-4);n<5;n++){
            basecolor += (texture2D(texture1, texcoord+(m*0.002, n*0.0037)) * 0.0025);
        };
    }};
    return basecolor;}""",
    """color = vcrshade(color);""")

SCANLINE_SHADER = ("""
vec4 scanlineshade(vec4 color) {
    return color * (0.98+0.02*sin(10.0*time-texcoord.y*2000.0));}""",
    """color = scanlineshade(color);""")

NTSC_SHADER = ("""

const mat3 myiq2rgb = mat3(
   1.0, 0.956, 0.621,
   1.0, -0.272, -0.647,
   1.0, -1.106, 1.703
);

vec3 yiq2rgb(vec3 yiq)
{
   return (yiq * myiq2rgb);
}

const mat3 mrgb2yiq = mat3(
      0.299, 0.587, 0.114,
      0.596, -0.274, -0.322,
      0.211, -0.523, 0.312
);

vec3 rgb2yiq(vec3 col)
{
   return (col * mrgb2yiq);
}

vec4 ntscshade(vec4 color) {
    vec3 basecolor = color.rgb;
    basecolor = rgb2yiq(basecolor);
    vec3 adj = rgb2yiq(texture2D(texture1, vec2(texcoord.x + step.x, texcoord.y)).rgb);
    basecolor.g = mix(basecolor.g, adj.g, 0.5);
    basecolor.b = mix(basecolor.b, adj.b, 0.5);
    adj = rgb2yiq(texture2D(texture1, vec2(texcoord.x - step.x, texcoord.y)).rgb);
    basecolor.g = mix(basecolor.g, adj.g, 0.5);
    basecolor.b = mix(basecolor.b, adj.b, 0.5);
    adj = rgb2yiq(texture2D(texture1, vec2(texcoord.x + (step.x*2.0), texcoord.y)).rgb);
    basecolor.g = mix(basecolor.g, adj.g, 0.2);
    basecolor.b = mix(basecolor.b, adj.b, 0.2);
    adj = rgb2yiq(texture2D(texture1, vec2(texcoord.x - (step.x*2.0), texcoord.y)).rgb);
    basecolor.g = mix(basecolor.g, adj.g, 0.2);
    basecolor.b = mix(basecolor.b, adj.b, 0.2);
    basecolor = yiq2rgb(basecolor);
    return vec4(basecolor.r, basecolor.g, basecolor.b, color.a);}""",
    """color = ntscshade(color);""")
