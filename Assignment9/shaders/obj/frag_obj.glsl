#version 420 core

in vec3 fragNormal;
in vec3 fragPos;
in vec2 fragUV;

uniform vec3 eyePos;
layout (binding=1) uniform sampler2D tex2D;
layout (binding=0) uniform samplerCube cubeMapTex;
uniform int textureType;

out vec4 outColor;

void main(){
    vec3 N = normalize(fragNormal);
    vec3 V = normalize(eyePos - fragPos);
    vec3 R = reflect(-V, N);

    R.z *= -1.0;

    vec3 envColor = texture(cubeMapTex, R).rgb;
    vec3 texColor = texture(tex2D, fragUV).rgb;

    if(textureType == 0)            outColor = vec4(envColor, 1.0);
    else if(textureType == 1)       outColor = vec4(texColor, 1.0);
    else if(textureType == 2)       outColor = mix(vec4(texColor, 1.0), vec4(envColor, 1.0), 0.2);
    else                            outColor = vec4(abs(N), 1.0);
}