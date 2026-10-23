// Copyright 2022 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#version 450 core
#extension GL_ARB_separate_shader_objects : enable

layout (location = 0) in vec2 frag_tex_coord;
layout (location = 0) out vec4 color;

layout (push_constant, std140) uniform DrawInfo {
    mat4 modelview_matrix;
    vec4 i_resolution;
    vec4 o_resolution;
    int screen_id_l;
    int screen_id_r;
    int layer;
    int reverse_interlaced;
};

layout (set = 0, binding = 0) uniform sampler2D screen_textures[3];


#ifdef THORDS_EDGE_AA
vec3 aaRead(sampler2D tex, vec2 uv) {
    ivec2 size = textureSize(tex, 0);
    vec2 pos = uv * vec2(size) - 0.5;
    ivec2 base = ivec2(floor(pos));
    vec2 weight = fract(pos);
    ivec2 hi = size - ivec2(1);
    vec3 a = texelFetch(tex, clamp(base, ivec2(0), hi), 0).rgb;
    vec3 b = texelFetch(tex, clamp(base + ivec2(1,0), ivec2(0), hi), 0).rgb;
    vec3 c = texelFetch(tex, clamp(base + ivec2(0,1), ivec2(0), hi), 0).rgb;
    vec3 d = texelFetch(tex, clamp(base + ivec2(1,1), ivec2(0), hi), 0).rgb;
    return mix(mix(a,b,weight.x), mix(c,d,weight.x), weight.y);
}
float aaLuma(vec3 rgb) { return dot(rgb, vec3(0.299, 0.587, 0.114)); }
vec4 ApplyEdgeAA(sampler2D tex, vec2 uv) {
    vec2 pixel = 1.0 / vec2(textureSize(tex, 0));
    vec4 original = texture(tex, uv);
    float center = aaLuma(original.rgb);
    float nw = aaLuma(texture(tex, uv + pixel * vec2(-1,-1)).rgb);
    float ne = aaLuma(texture(tex, uv + pixel * vec2( 1,-1)).rgb);
    float sw = aaLuma(texture(tex, uv + pixel * vec2(-1, 1)).rgb);
    float se = aaLuma(texture(tex, uv + pixel * vec2( 1, 1)).rgb);
    float low = min(center, min(min(nw,ne),min(sw,se)));
    float high = max(center, max(max(nw,ne),max(sw,se)));
    if (high-low < max(0.04, high*0.125)) {
        return original;
    }
    vec2 tangent = vec2(sw+se-nw-ne, nw+sw-ne-se);
    float guard = max((nw+ne+sw+se)*0.03125, 0.0078125);
    tangent = clamp(tangent / (min(abs(tangent.x),abs(tangent.y))+guard),
                    vec2(-4.0),vec2(4.0)) * pixel;
    vec3 inner = 0.5 * (aaRead(tex, uv-tangent/6.0)+aaRead(tex, uv+tangent/6.0));
    vec3 outer = 0.5*inner + 0.25*(aaRead(tex, uv-tangent*0.5)+aaRead(tex, uv+tangent*0.5));
    float filtered = aaLuma(outer);
    vec3 result = (filtered < low || filtered > high) ? inner : outer;
    return vec4(mix(original.rgb,result,0.75), original.a);
}

#define ReadScreen(tex) ApplyEdgeAA(tex, frag_tex_coord)
#else
#define ReadScreen(tex) texture(tex, frag_tex_coord)
#endif

vec4 GetScreen(int screen_id) {
#ifdef ARRAY_DYNAMIC_INDEX
    return ReadScreen(screen_textures[screen_id]);
#else
    switch (screen_id) {
    case 0:
        return ReadScreen(screen_textures[0]);
    case 1:
        return ReadScreen(screen_textures[1]);
    case 2:
        return ReadScreen(screen_textures[2]);
    }
#endif
}

void main() {
    color = GetScreen(screen_id_l);
}
