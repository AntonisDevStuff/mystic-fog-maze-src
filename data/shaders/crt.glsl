#version 330 core

uniform sampler2D image;

out vec4 color;
in vec2 fragmentTexCoord;

const float CURVATURE = 4.0;
const float VIGNETTE_MULTIPLIER = 1.25;

const float SCANLINE_DENSITY = 140.0;
const float SCANLINE_INTENSITY = 0.045;

const float ABERRATION_STRENGTH = 0.055;

const float GLOW_SPREAD = 0.0025;
const float GLOW_MIX = 0.16;

// Precalculate constants
const vec3 LUMA = vec3(0.299, 0.587, 0.114);
const float INV_CURVATURE = 1.0 / CURVATURE;
const float SCANLINE_FACTOR = 2.0 * SCANLINE_DENSITY;
const float SCANLINE_BASE = 1.0 - SCANLINE_INTENSITY;
const float GLOW_DIAGONAL_WEIGHT = 0.5;
const float GLOW_DIVISOR = 1.0 / 6.0;

float luminance(vec3 col) {
    return dot(col, LUMA);
}

vec2 applyCurvature(vec2 uv) {
    vec2 centered_uv = uv * 2.0 - 1.0;
    vec2 uv_offset = centered_uv.yx * INV_CURVATURE;
    centered_uv += centered_uv * uv_offset * uv_offset;
    return centered_uv * 0.5 + 0.5;
}

bool isOutOfBounds(vec2 uv) {
    vec2 centered = abs(uv * 2.0 - 1.0);
    return centered.x > 1.0 || centered.y > 1.0;
}

float vignette(vec2 uv) {
    vec2 centered_uv = uv * 2.0 - 1.0;
    vec2 powered = pow(abs(centered_uv), vec2(4.0));
    return length(powered * 0.333333);
}

float scanline(vec2 uv) {
    float warped_y = uv.y * 2.0 - 1.0;
    return sin(warped_y * SCANLINE_FACTOR) * SCANLINE_INTENSITY + SCANLINE_BASE;
}

vec3 chromaticAberration(sampler2D tex, vec2 uv) {
    vec2 dir = uv - 0.5;
    float strength = dot(dir, dir) * ABERRATION_STRENGTH;
    vec2 offset = dir * strength;

    float r = texture(tex, clamp(uv + offset, 0.0, 1.0)).r;
    float g = texture(tex, uv).g;
    float b = texture(tex, clamp(uv - offset, 0.0, 1.0)).b;

    vec3 base = vec3(r, g, b);
    vec3 original = texture(tex, uv).rgb;

    float aberLum = luminance(base);
    float origLum = luminance(original);

    return original * (aberLum / max(origLum, 0.0001));
}

vec3 phosphorGlow(sampler2D tex, vec2 uv) {
    vec2 offsetX = vec2(GLOW_SPREAD, 0.0);
    vec2 offsetY = vec2(0.0, GLOW_SPREAD);

    vec3 glow = texture(tex, clamp(uv + offsetX, 0.0, 1.0)).rgb;
    glow += texture(tex, clamp(uv - offsetX, 0.0, 1.0)).rgb;
    glow += texture(tex, clamp(uv + offsetY, 0.0, 1.0)).rgb;
    glow += texture(tex, clamp(uv - offsetY, 0.0, 1.0)).rgb;

    glow += texture(tex, clamp(uv + offsetX + offsetY, 0.0, 1.0)).rgb * GLOW_DIAGONAL_WEIGHT;
    glow += texture(tex, clamp(uv - offsetX + offsetY, 0.0, 1.0)).rgb * GLOW_DIAGONAL_WEIGHT;
    glow += texture(tex, clamp(uv + offsetX - offsetY, 0.0, 1.0)).rgb * GLOW_DIAGONAL_WEIGHT;
    glow += texture(tex, clamp(uv - offsetX - offsetY, 0.0, 1.0)).rgb * GLOW_DIAGONAL_WEIGHT;

    vec3 base = texture(tex, uv).rgb;
    float glowLum = luminance(glow * GLOW_DIVISOR);
    float baseLum = luminance(base);
    float boost = mix(1.0, glowLum / max(baseLum, 0.0001), GLOW_MIX);

    return base * boost;
}

void main() {
    vec2 uv = applyCurvature(fragmentTexCoord);

    if (isOutOfBounds(uv)) {
        color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec3 base = chromaticAberration(image, uv);
    vec3 col = phosphorGlow(image, uv);

    float colLum = luminance(col);
    float baseLum = luminance(base);
    col = mix(col, col * (baseLum / max(colLum, 0.0001)), step(0.0001, baseLum));
    col = mix(base, col, 0.5);

    col *= scanline(uv);
    col -= vignette(uv) * VIGNETTE_MULTIPLIER;

    color = vec4(col, 1.0);
}
