import pygame as pg
from OpenGL.GL import *
import numpy as np
import shaderLoaderV3
from objLoaderV4 import ObjLoader
from utils import load_image
from guiV3 import SimpleGUI
import pyrr
import os

def load_cubemap_texture(filenames):
    # Generate a texture ID
    texture_id = glGenTextures(1)

    # Bind the texture as a cubemap
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)

    # Define texture parameters
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


    # Define the faces of the cubemap
    faces = [GL_TEXTURE_CUBE_MAP_POSITIVE_X, GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
             GL_TEXTURE_CUBE_MAP_POSITIVE_Y, GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
             GL_TEXTURE_CUBE_MAP_POSITIVE_Z, GL_TEXTURE_CUBE_MAP_NEGATIVE_Z]

    # Load and bind images to the corresponding faces
    for i in range(6):
        img_data, img_w, img_h = load_image(filenames[i], format="RGB", flip=False)
        glTexImage2D(faces[i], 0, GL_RGB, img_w, img_h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

    # Generate mipmaps
    # glGenerateMipmap(GL_TEXTURE_CUBE_MAP)

    # Unbind the texture
    glBindTexture(GL_TEXTURE_CUBE_MAP, 0)

    return texture_id



def load_2d_texture(filename):
    img_data, img_w, img_h = load_image(filename, format="RGB", flip=True)

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # Set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)  # Set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_w, img_h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id



# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 1280
height = 720
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


# Set the background color (clear color)
# glClearColor takes 4 arguments: red, green, blue, alpha. Each argument is a float between 0 and 1.
glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)


# Camera parameters
eye = (0,0,2)
target = (0,0,0)
up = (0,1,0)

fov = 45
aspect = width/height
near = 0.1
far = 10

view_mat  = pyrr.matrix44.create_look_at(eye, target, up)
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)



# Write our shaders. We will write our vertex shader and fragment shader in a different file
shaderProgram_obj = shaderLoaderV3.ShaderProgram("shaders/obj/vert_obj.glsl", "shaders/obj/frag_obj.glsl")
shaderProgram_skybox = shaderLoaderV3.ShaderProgram("shaders/skybox/vert_skybox.glsl", "shaders/skybox/frag_skybox.glsl")



'''
# **************************************************************************************************************
# Setup vertices, VAO, VBO, and vertex attributes for the object
# **************************************************************************************************************
'''
# Lets load our objects
obj = ObjLoader("objects//rayman/raymanModel.obj")

# *********** Lets define model matrix ***********
translation_mat = pyrr.matrix44.create_from_translation(-obj.center)
scaling_mat = pyrr.matrix44.create_from_scale([2 / obj.dia, 2 / obj.dia, 2 / obj.dia])
model_mat = pyrr.matrix44.multiply(translation_mat, scaling_mat)

# VAO and VBO
vao_obj = glGenVertexArrays(1)
glBindVertexArray(vao_obj)
vbo_obj = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo_obj)
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)

# Define the vertex attribute configurations
# we can either query the locations of the attributes in the shader like we did in our previous assignments
# or explicitly tell the shader that the attribute "position" corresponds to location 0.
# It is recommended to explicitly set the locations of the attributes in the shader than querying them.
# Position attribute
position_loc = 0
glBindAttribLocation(shaderProgram_obj.shader, position_loc, "position")
glVertexAttribPointer(position_loc, obj.size_position, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_position))
glEnableVertexAttribArray(position_loc)

tex_coord_loc = 1
glBindAttribLocation(shaderProgram_obj.shader, tex_coord_loc, "uv")
glVertexAttribPointer(tex_coord_loc, obj.size_texture, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_texture))
glEnableVertexAttribArray(tex_coord_loc)

normal_loc = 2
glBindAttribLocation(shaderProgram_obj.shader, normal_loc, "normal")
glVertexAttribPointer(normal_loc, obj.size_normal, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_normal))
glEnableVertexAttribArray(normal_loc)
# **************************************************************************************************************
# **************************************************************************************************************


'''
# **************************************************************************************************************
# Set up vertices, VAO, VBO, and vertex attributes for a quad that will be used to render the skybox
# **************************************************************************************************************
'''
# Define the vertices of the quad.
quad_vertices = (
            # Position
            -1, -1,
             1, -1,
             1,  1,
             1,  1,
            -1,  1,
            -1, -1
)
vertices = np.array(quad_vertices, dtype=np.float32)

size_position = 2       # x, y, z
stride = size_position * 4
offset_position = 0
quad_n_vertices = len(vertices) // size_position  # number of vertices

# Create VA0 and VBO
vao_quad = glGenVertexArrays(1)
glBindVertexArray(vao_quad)            # Bind the VAO. That is, make it the active one.
vbo_quad = glGenBuffers(1)                  # Generate one buffer and store its ID.
glBindBuffer(GL_ARRAY_BUFFER, vbo_quad)     # Bind the buffer. That is, make it the active one.
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)   # Upload the data to the GPU.

# Define the vertex attribute configurations
# we can either query the locations of the attributes in the shader like we did in our previous assignments
# or explicitly tell the shader that the attribute "position" corresponds to location 0.
# It is recommended to explicitly set the locations of the attributes in the shader than querying them.
# Position attribute
position_loc = 0
glBindAttribLocation(shaderProgram_skybox.shader, position_loc, "position")
glVertexAttribPointer(position_loc, size_position, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset_position))
glEnableVertexAttribArray(position_loc)

# **************************************************************************************************************
# **************************************************************************************************************



'''
# **************************************************************************************************************
# Load the 2D texture and attach the sampler variable "tex" in the object shader to texture unit 0.
# **************************************************************************************************************
'''
obj_tex_id = load_2d_texture("objects/rayman/raymanModel.png")

# shaderProgram_obj["tex2D"] = 1   # Okay this might be confusing. Here 0 indicates texture unit 0. Note that "tex" is a sampler variable in the fragment shader. It is not an integer.
# **************************************************************************************************************
# **************************************************************************************************************





'''
# **************************************************************************************************************
# Load the cubemap texture and attach the sampler variable "cubeMapTex" in both shaders to texture unit 0.
# **************************************************************************************************************
'''
dir = "images/skybox"
cubemap_images = ["right.png", "left.png", "top.png", "bottom.png", "front.png", "back.png"]
cubemap_images = [os.path.join(dir, img) for img in cubemap_images]
cubemap_id = load_cubemap_texture(cubemap_images)

# shaderProgram_skybox["cubeMapTex"] = 0
# shaderProgram_obj["cubeMapTex"] = 0

# **************************************************************************************************************
# **************************************************************************************************************





gui = SimpleGUI("Skybox")

# Create a slider for the rotation angle around the Z axis
camera_rotY_slider = gui.add_slider("camera Y angle", -180, 180, 0, resolution=1)
camera_rotX_slider = gui.add_slider("camera X angle", -90, 90, 0, resolution=1)
fov_slider = gui.add_slider("fov", 25, 120, 45, resolution=1)

texture_type_radio = gui.add_radio_buttons("Texture type:",
                      options_dict={"Environment mapping": 0, "2D texture": 1, "Mix": 2},
                      initial_option="Environment mapping")





# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear color buffer and depth buffer before drawing each frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rotateY_mat = pyrr.matrix44.create_from_y_rotation(np.deg2rad(camera_rotY_slider.get_value()))
    rotateX_mat = pyrr.matrix44.create_from_x_rotation(np.deg2rad(camera_rotX_slider.get_value()))
    rotation_mat = pyrr.matrix44.multiply(rotateX_mat, rotateY_mat)
    rotated_eye = pyrr.matrix44.apply_to_vector(rotation_mat, eye)

    view_mat = pyrr.matrix44.create_look_at(rotated_eye, target, up)
    projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_slider.get_value(),
                                                                        aspect, near,  far)

    # remove the translation component from the view matrix because we want the skybox to be static
    view_mat_without_translation = view_mat.copy()
    view_mat_without_translation[3][:3] = [0,0,0]

    # compute the inverse of the view (one without translation)- projection matrix
    inverseViewProjection_mat = pyrr.matrix44.inverse(pyrr.matrix44.multiply(view_mat_without_translation,projection_mat))

    '''
    # ******************* Draw the object ************************
    '''
    # ***** Set Uniforms *****
    glUseProgram(shaderProgram_obj.shader)   # being explicit even though the line below will call this function
    shaderProgram_obj["modelMatrix"] = model_mat
    shaderProgram_obj["viewMatrix"] = view_mat
    shaderProgram_obj["projectionMatrix"] = projection_mat
    shaderProgram_obj["eyePos"] = rotated_eye

    texture_type = int(texture_type_radio.get_value())
    shaderProgram_obj["textureType"] = texture_type

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap_id)

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, obj_tex_id)

    # ***** Draw *****
    glBindVertexArray(vao_obj)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)      # Draw the triangle
    '''
    # *************************************************************
    '''


    '''
    # ******************* Draw the skybox ************************
    '''
    glDepthFunc(GL_LEQUAL)  # Change depth function so depth test passes when values are equal to depth buffer's content

    # ***** Set Uniforms *****
    glUseProgram(shaderProgram_skybox.shader)   # being explicit even though the line below will call this function
    shaderProgram_skybox["invViewProjectionMatrix"] = inverseViewProjection_mat

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap_id)

    # ***** Draw *****
    glBindVertexArray(vao_quad)
    glDrawArrays(GL_TRIANGLES,
                 0,
                 quad_n_vertices)  # Draw the triangle

    glDepthFunc(GL_LESS)    # Set depth function back to default
    '''
    # *************************************************************
    '''



    # Refresh the display to show what's been drawn
    pg.display.flip()


# Cleanup
glDeleteVertexArrays(1, [vao_obj, vao_quad])
glDeleteBuffers(1, [vbo_obj, vbo_quad])

glDeleteProgram(shaderProgram_obj.shader)
glDeleteProgram(shaderProgram_skybox.shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program