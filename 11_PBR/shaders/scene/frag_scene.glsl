#version 420 core


#define PI 3.1415926538

in vec2 fragUV;
in vec3 fragPos;
in vec3 fragNormal;

out vec4 outColor;

uniform vec3 eyePos;
uniform vec3 lightPos;
uniform float roughness;
uniform float metallic;
uniform float ambientIntensity;
uniform vec3 materialColor;
uniform vec3 lightColor;


// Lambertian diffuse BRDF
vec3 computeDiffuseColor(vec3 N, vec3 L)
{
    return materialColor * clamp(dot(N,L), 0.0, 1.0);
}

// GGX normal distribution function
float D_GGX(float NoH, float a) {
    float a2 = a * a;
    float denom = PI * pow(NoH * NoH * (a2 - 1.0) + 1.0, 2.0);
    return a2 / denom;
}

// Schlick's approximation of the Fresnel coefficient
vec3 F_Schlick(float u, vec3 f0) {
    return f0 + (vec3(1.0) - f0) * pow(1.0 - u, 5.0);
}

// Smith's correlated GGX visibility function
float V_SmithGGXCorrelated(float NoV, float NoL, float a) {
//     float k = (a + 1.0) * (a + 1.0) / 8.0;      // This is how they used to define k in UE4. They have changed it.
    float k = a / 2.0;
    float GGXL = NoV / (NoV * (1.0 - k) + k);
    float GGXV = NoL / (NoL * (1.0 - k) + k);
    return GGXL * GGXV;
}


void main(){
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(lightPos - fragPos);
    vec3 V = normalize(eyePos - fragPos);
    vec3 H = normalize(L + V);

    float NoV = abs(dot(N, V)) + 1e-5;
    float NoL = clamp(dot(N, L), 0.0, 1.0);
    float NoH = clamp(dot(N, H), 0.0, 1.0);
    float LoH = clamp(dot(L, H), 0.0, 1.0);

    float distance = length(lightPos - fragPos);
    vec3 radiance = lightColor;

    // perceptually linear roughness to roughness (see parameterization)
    float alpha = roughness * roughness;
    alpha = max(alpha, 0.01);

    vec3 f0 = vec3(0.04);            // default to reflectance of 4% (roughly 0.5% for dielectrics)
    f0 = mix(f0, materialColor, metallic);

    vec3  F = F_Schlick(LoH, f0);
    float Dggx = D_GGX(NoH, alpha);
    float Vggx = V_SmithGGXCorrelated(NoV, NoL, alpha);

    vec3 ks = F;
    vec3 kd = vec3(1.0) - ks;

    vec3 ambientColor = materialColor * ambientIntensity;
    vec3 diffuseColor = kd * (1-metallic) * computeDiffuseColor(N, L);
    vec3 specularBRDF = (Dggx * F * Vggx);

    vec3 finalColor = ambientColor + diffuseColor + specularBRDF * lightColor;

    outColor = vec4(finalColor, 1.0);
}