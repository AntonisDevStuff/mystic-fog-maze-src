#version 330 core
uniform sampler2D image;

out vec4 color;
in vec2 fragmentTexCoord;

const float CURVE_STRENGTH = 2.5;
const float CURVE_POWER = 5.5;

const float ABERRATION = 0.002;

const float SCANLINE_FREQUENCY = 400.0;
const float SCANLINE_INTENSITY = 0.08;

const float VIGNETTE_SCALE = 16.0;
const float VIGNETTE_POWER = 0.3;

const float GLOW_SPREAD = 0.0015;
const float GLOW_INTENSITY = 0.35;

const float PHOSPHOR_GRID_SCALE = 400.0;
const float PHOSPHOR_INTENSITY = 0.05;

vec3 sampleWithGlow(sampler2D tex, vec2 uv) {
    vec3 center = texture(tex, uv).rgb;
    vec3 glow = vec3(0.0);

    glow += texture(tex, uv + vec2( GLOW_SPREAD, 0.0)).rgb;
    glow += texture(tex, uv + vec2(-GLOW_SPREAD, 0.0)).rgb;
    glow += texture(tex, uv + vec2(0.0,  GLOW_SPREAD)).rgb;
    glow += texture(tex, uv + vec2(0.0, -GLOW_SPREAD)).rgb;

    return center + (glow / 4.0) * GLOW_INTENSITY;
}

void main() {
    vec2 center = vec2(0.5, 0.5);
    vec2 off_center = fragmentTexCoord - center;

    off_center *= 1.0 + CURVE_STRENGTH * pow(abs(off_center.yx), vec2(CURVE_POWER));

    vec2 uv = center + off_center;

    if (uv.x > 1.0 || uv.x < 0.0 || uv.y > 1.0 || uv.y < 0.0) {
        color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    float r = sampleWithGlow(image, uv + vec2( ABERRATION, 0.0)).r;
    float g = sampleWithGlow(image, uv).g;
    float b = sampleWithGlow(image, uv - vec2( ABERRATION, 0.0)).b;

    vec3 col = vec3(r, g, b);

    float scanline = sin(uv.y * SCANLINE_FREQUENCY) * SCANLINE_INTENSITY;
    col -= scanline;

    float phosphorX = sin(uv.x * PHOSPHOR_GRID_SCALE) * PHOSPHOR_INTENSITY;
    float phosphorY = sin(uv.y * PHOSPHOR_GRID_SCALE * 3.0) * PHOSPHOR_INTENSITY;
    col -= (phosphorX + phosphorY) * 0.5;

    float vignette = uv.x * uv.y * (1.0 - uv.x) * (1.0 - uv.y);
    vignette = clamp(pow(vignette * VIGNETTE_SCALE, VIGNETTE_POWER), 0.0, 1.0);
    col *= vignette;

    col = clamp(col * 1.1, 0.0, 1.0);

    color = vec4(col, 1.0);
}
