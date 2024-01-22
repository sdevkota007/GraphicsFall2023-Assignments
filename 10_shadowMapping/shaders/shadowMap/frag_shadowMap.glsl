#version 420 core

out vec4 outColor;

void main(){
//    outColor = vec4(vec3(0.0), 1.0);
    outColor = vec4(vec3(gl_FragCoord.z),1.0);
}