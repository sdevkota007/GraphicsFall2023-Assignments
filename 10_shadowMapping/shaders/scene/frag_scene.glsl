#version 420 core


in vec2 fragUV;
in vec3 fragPos;
in vec3 fragNormal;
in vec4 fragPos_LightSpace;

layout (binding=0) uniform sampler2D depthTex;

uniform vec3 lightPos;
uniform bool isPcf;
uniform int nPCF;

uniform mat4 lightViewMatrix;
uniform mat4 lightProjectionMatrix;

uniform vec3 materialColor;

out vec4 outColor;


vec3 computeDiffuseColor(vec3 N, vec3 L)
{
    return materialColor * clamp(dot(N,L), 0.0, 1.0);
}


float computeEpsilon(vec3 N, vec3 L)
{
    return max(0.0005f * (1.0 - dot(N, L)), 0.0001f);
}

float computePCF(float z_current, float epsilon, vec2 texCoord)
{
    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(depthTex, 0);
    for(int x = -nPCF; x <= nPCF; ++x)
    {
        for(int y = -nPCF; y <= nPCF; ++y)
        {
            float pcfDepth = texture(depthTex, texCoord + vec2(x, y) * texelSize).r;
            shadow += z_current - epsilon > pcfDepth  ? 1.0 : 0.0;
        }
    }
    shadow /= pow(2.0 * nPCF + 1.0, 2.0);

    return shadow;
}


float computeShadowFactor(vec3 N, vec3 L)
{
    //transform from homogeneous coordinates to 3D coordinates.
    vec3 pos_lightSpace = fragPos_LightSpace.xyz/fragPos_LightSpace.w;

    // transform from [-1,1] to [0,1]
    pos_lightSpace = (pos_lightSpace + 1.0)/2.0;

    // get the z value from light point of view
    float z_current = pos_lightSpace.z;

    // get the depth value from the depth texture
    float depth_lightPov = texture(depthTex, pos_lightSpace.xy).r;

    // calculate bias (based on depth map resolution and slope)
    float epsilon = computeEpsilon(N, L);
    epsilon = 0.0005f;

    // Apply either PCF or simple shadow test
    float shadow = 0.0;
    if(isPcf)      shadow = computePCF(z_current, epsilon, pos_lightSpace.xy);
    else           shadow = z_current - epsilon > depth_lightPov  ? 1.0 : 0.0;

    // keep the shadow at 0.0 when outside the far_plane region of the light's frustum.
    if(z_current > 1.0)
        shadow = 0.0;

    return shadow;
}

void main(){
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(lightPos - fragPos);

    vec3 diffuseColor = computeDiffuseColor(N, L);
    float shadow = computeShadowFactor(N, L);

    outColor = vec4(diffuseColor * (1-shadow), 1.0);
}