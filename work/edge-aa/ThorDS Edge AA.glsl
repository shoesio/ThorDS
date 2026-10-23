// ThorDS directional edge anti-aliasing for Azahar's Dolphin-compatible shader API.
// Keep flat regions untouched. Explicit bilinear reads let edge filtering work
// even when the final presentation sampler uses nearest-neighbour filtering.
vec3 aaRead(vec2 uv) {
    ivec2 size = textureSize(color_texture, 0);
    vec2 pos = uv * vec2(size) - 0.5;
    ivec2 base = ivec2(floor(pos));
    vec2 weight = fract(pos);
    ivec2 hi = size - ivec2(1);
    vec3 a = texelFetch(color_texture, clamp(base, ivec2(0), hi), 0).rgb;
    vec3 b = texelFetch(color_texture, clamp(base + ivec2(1,0), ivec2(0), hi), 0).rgb;
    vec3 c = texelFetch(color_texture, clamp(base + ivec2(0,1), ivec2(0), hi), 0).rgb;
    vec3 d = texelFetch(color_texture, clamp(base + ivec2(1,1), ivec2(0), hi), 0).rgb;
    return mix(mix(a,b,weight.x), mix(c,d,weight.x), weight.y);
}
float aaLuma(vec3 rgb) { return dot(rgb, vec3(0.299, 0.587, 0.114)); }
void main() {
    vec2 uv = GetCoordinates();
    vec2 pixel = 1.0 / vec2(textureSize(color_texture, 0));
    vec4 original = Sample();
    float center = aaLuma(original.rgb);
    float nw = aaLuma(SampleLocation(uv + pixel * vec2(-1,-1)).rgb);
    float ne = aaLuma(SampleLocation(uv + pixel * vec2( 1,-1)).rgb);
    float sw = aaLuma(SampleLocation(uv + pixel * vec2(-1, 1)).rgb);
    float se = aaLuma(SampleLocation(uv + pixel * vec2( 1, 1)).rgb);
    float low = min(center, min(min(nw,ne),min(sw,se)));
    float high = max(center, max(max(nw,ne),max(sw,se)));
    if (high-low < max(0.04, high*0.125)) {
        SetOutput(original);
        return;
    }
    vec2 tangent = vec2(sw+se-nw-ne, nw+sw-ne-se);
    float guard = max((nw+ne+sw+se)*0.03125, 0.0078125);
    tangent = clamp(tangent / (min(abs(tangent.x),abs(tangent.y))+guard),
                    vec2(-4.0),vec2(4.0)) * pixel;
    vec3 inner = 0.5 * (aaRead(uv-tangent/6.0)+aaRead(uv+tangent/6.0));
    vec3 outer = 0.5*inner + 0.25*(aaRead(uv-tangent*0.5)+aaRead(uv+tangent*0.5));
    float filtered = aaLuma(outer);
    vec3 result = (filtered < low || filtered > high) ? inner : outer;
    SetOutput(vec4(mix(original.rgb,result,0.75), original.a));
}
