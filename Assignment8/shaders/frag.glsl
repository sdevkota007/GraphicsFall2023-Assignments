#version 330 core

out vec4 outColor;

in vec3 fragNormal;

// todo: 4
in vec3 fragPosition;

// todo: 5
uniform vec4 light_pos;
uniform vec3 eye_pos;
uniform vec3 material_color;

vec3 brightColor = vec3(1.0);
vec3 blackColor = vec3(0.0);

uniform int shading_mode;
uniform bool isSilhouette;
uniform bool isSmooth;

float _smoothstep(float edge0, float edge1, float x)
{
    float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

vec3 computeDiffuse(vec3 N, vec3 L){
      return material_color * clamp(dot(L,N), 0.,1.);
}

vec3 toonShade1(vec3 N, vec3 L)
{
    float intensity = 0.0;
    float threshold = 0.0;
    if(dot(N, L) > 0.85)        intensity = 1.0;
    else if(dot(N, L) > 0.5)    intensity = 0.7;
    else if(dot(N, L) > 0.25)   intensity = 0.5;
    else if(dot(N, L) > 0.1)    intensity = 0.3;
    else                        intensity = 0.1;


    return material_color * intensity;
}


vec3 toonShade2(vec3 N, vec3 L)
{
    // Calculate the diffuse term
    float intensity = clamp(dot(N, L), 0.0, 1.0);

    // Choose number of steps in the toon shading
    float levels = 4.0;

    if(isSmooth){
        float step = sqrt(intensity) * levels;
        intensity = (floor(step) + _smoothstep(0.48, 0.52, fract(step))) / levels;
        intensity = intensity * intensity;
    }
    else
    {
        intensity = ceil(intensity * levels)/levels;
    }

    vec3 color = material_color * intensity;

    return color;
}


void main(){
    // todo: 7
    vec3 N = normalize(fragNormal);
    vec3 L;
    if (light_pos.w==0.0)   L = normalize(light_pos.xyz);                   // directional light
    else                    L = normalize(light_pos.xyz-fragPosition);      // point light
    vec3 V = normalize(eye_pos - fragPosition);
    vec3 H = normalize(V + L);


    vec3 color = vec3(0.0);
    if(shading_mode == 0)
    {
        color = computeDiffuse(N, L);
    }
    else
    {
        color = toonShade2(N, L);

        if (isSilhouette)
        {
            // for rim light
            if(dot(N,V) < 0.2)  color = blackColor;
        }

    }

    outColor = vec4(color, 1.0);
}