#version 330 core

in vec3 position; // Attribute
in vec3 normal;   // Attribute

uniform float scale;
uniform vec3 center;
uniform float aspect;

out vec3 fragNormal;

void main(){
    vec3 pos = (position - center);     // transform to center
    pos = pos * scale;                  // scale to fit screen
    pos.x /= aspect;                    // correct aspect ratio
    gl_Position = vec4(pos.x, pos.y, -pos.z, 1.0);
    fragNormal = normalize(normal);
}