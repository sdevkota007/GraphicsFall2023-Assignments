#version 330 core

out vec4 outColor;

in vec3 fragNormal;
in vec3 fragPosition;

uniform vec4 light_pos;
uniform vec3 eye_pos;

uniform vec3 material_color;
uniform float ambient_intensity;
uniform vec3 specular_color;
uniform int shininess;
uniform float K_s;

uniform int object_id;

int LEFT = -1;
int MIDDLE = 0;
int RIGHT = 1;

vec3 computeDiffuse(vec3 N, vec3 L){
      return material_color * clamp(dot(L,N), 0.,1.);
}

vec3 computeSpecular(vec3 N, vec3 L, vec3 V){
      vec3 H = normalize(L+V);
      float dotNH = clamp(dot(N,H),0.,1.);
      return specular_color * pow(dotNH, shininess);
}

vec3 computeAmbient(){
      return material_color * ambient_intensity;
}


void main(){
      vec3 N = normalize(fragNormal);
      vec3 L;
      if (light_pos.w==0.0)   L = normalize(light_pos.xyz);                   // directional light
      else                    L = normalize(light_pos.xyz-fragPosition);      // point light

      vec3 V = normalize(eye_pos-fragPosition);

      vec3 difuse = computeDiffuse(N, L);
      vec3 specular = computeSpecular(N, L, V);
      vec3 ambient = computeAmbient();

      vec3 color = vec3(1.0, 1.0, 1.0);

      if(object_id == LEFT)             color = difuse;
      else if(object_id == MIDDLE)      color = specular;
      else if(object_id == RIGHT)       color = ambient + difuse + K_s*specular;

      outColor = vec4(color, 1.0);
}