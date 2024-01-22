import pygame as pg
from OpenGL.GL import *
import numpy as np
import shaderLoaderV3
from objLoaderV4 import ObjLoader
from utils import load_image
from guiV3 import SimpleGUI
import pyrr
import os

def upload_and_configure_attributes(object, shader):
    # VAO and VBO
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, object.vertices.nbytes, object.vertices, GL_STATIC_DRAW)

    # Define the vertex attribute configurations
    # we can either query the locations of the attributes in the shader like we did in our previous assignments
    # or explicitly tell the shader that the attribute "position" corresponds to location 0.
    # It is recommended to explicitly set the locations of the attributes in the shader than querying them.
    # Position attribute
    position_loc = 0
    tex_coord_loc = 1
    normal_loc = 2
    glVertexAttribPointer(position_loc, object.size_position, GL_FLOAT, GL_FALSE, object.stride, ctypes.c_void_p(object.offset_position))
    glVertexAttribPointer(tex_coord_loc, object.size_texture, GL_FLOAT, GL_FALSE, object.stride, ctypes.c_void_p(object.offset_texture))
    glVertexAttribPointer(normal_loc, object.size_normal, GL_FLOAT, GL_FALSE, object.stride, ctypes.c_void_p(object.offset_normal))

    glEnableVertexAttribArray(tex_coord_loc)
    glEnableVertexAttribArray(position_loc)
    glEnableVertexAttribArray(normal_loc)

    return vao, vbo, object.n_vertices


def load_cubemap_texture(filenames):
    # Generate a texture ID
    texture_id = glGenTextures(1)

    # Bind the texture as a cubemap
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)

    # Define texture parameters
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
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
    glGenerateMipmap(GL_TEXTURE_CUBE_MAP)

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




def render_scene():
    '''
    This function renders the scene from the camera's point of view.
    :return:
    '''
    # ***** Set Uniforms *****
    glUseProgram(shaderProgram_scene.shader)   # being explicit even though the line below will call this function
    shaderProgram_scene["viewMatrix"] = view_mat
    shaderProgram_scene["projectionMatrix"] = projection_mat

    materialColor = [float(k) for k in material_radiobutton.get_value().strip("()").split(",")]  # convert tuple to list
    shaderProgram_scene["materialColor"] = materialColor
    shaderProgram_scene["lightColor"] = light_color_slider.get_color()
    shaderProgram_scene["lightPos"] = rotated_lightPos
    shaderProgram_scene["eyePos"] = rotated_eye
    shaderProgram_scene["ambientIntensity"] = ambient_slider.get_value()
    shaderProgram_scene["roughness"] = roughness_slider.get_value()
    shaderProgram_scene["metallic"] = metallic_slider.get_value()



    # ***** Draw object *****
    shaderProgram_scene["modelMatrix"] = model_mat_obj
    glBindVertexArray(vao_obj)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)
    # ***********************




'''
# Program starts here
'''


# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_STENCIL_SIZE, 8)

# Create a window for graphics using OpenGL
width = 1280
height = 720
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)



# Set the background color (clear color)
# glClearColor takes 4 arguments: red, green, blue, alpha. Each argument is a float between 0 and 1.
glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)


# Write our shaders.
shaderProgram_scene = shaderLoaderV3.ShaderProgram("shaders/scene/vert_scene.glsl", "shaders/scene/frag_scene.glsl")


'''
# **************************************************************************************************************
# Load our objects and configure their attributes
# **************************************************************************************************************
'''
# obj = ObjLoader("objects/rayman/raymanModel.obj")
obj = ObjLoader("objects/dragon.obj")
vao_obj, vbo_obj, n_vertices_obj = upload_and_configure_attributes(obj, shaderProgram_scene.shader)

# **************************************************************************************************************
# **************************************************************************************************************



'''
# **************************************************************************************************************
# Define camera attributes
# **************************************************************************************************************
'''
eye = (0,0,2)
target = (0,0,0)
up = (0,1,0)

fov = 35
aspect = width/height
near = 0.1
far = 20

lightPos = [1, 4, 1]
# **************************************************************************************************************
# **************************************************************************************************************



'''
# **************************************************************************************************************
# Configure model matrices
# **************************************************************************************************************
'''
# for object
translation_mat = pyrr.matrix44.create_from_translation(-obj.center)
scaling_mat = pyrr.matrix44.create_from_scale([2 / obj.dia, 2 / obj.dia, 2 / obj.dia])
model_mat_obj = pyrr.matrix44.multiply(translation_mat, scaling_mat)

# **************************************************************************************************************
# **************************************************************************************************************


'''
# **************************************************************************************************************
# Setup gui
# **************************************************************************************************************
'''
gui = SimpleGUI("GUI")

# Create a slider for the rotation angle around the Y axis
light_rotY_slider = gui.add_slider("light Y angle", -180, 180, 0, resolution=1)

camera_rotY_slider = gui.add_slider("camera Y angle", -180, 180, 0, resolution=1)
camera_rotX_slider = gui.add_slider("camera X angle", -90, 90, 0, resolution=1)
fov_slider = gui.add_slider("fov", fov, 120, fov, resolution=1)



light_color_slider = gui.add_color_picker(label_text="Light Color", initial_color=(1, 1, 1))
ambient_slider = gui.add_slider("Ambient Intensity", 0, 1, 0.1, resolution=0.01)
roughness_slider = gui.add_slider("Roughness", 0, 1, 0.5, resolution=0.01)
metallic_slider = gui.add_slider("Metallic", 0, 1, 0.5, resolution=0.01)
material_radiobutton = gui.add_radio_buttons(label_text="Material",
                                             options_dict={"Iron":   (0.56, 0.57, 0.58),
                                                           "Copper": (0.95, 0.64, 0.54),
                                                           "Gold":   (1.00, 0.71, 0.29),
                                                           "Aluminium": (0.91, 0.92, 0.92),
                                                           "Silver": (0.95, 0.93, 0.88)},
                                             initial_option="Gold")

# **************************************************************************************************************
# **************************************************************************************************************



# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear color buffer and depth buffer before drawing each frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # view and projection matrices from the camera's point of view
    cam_rotY_mat = pyrr.matrix44.create_from_y_rotation(np.deg2rad(camera_rotY_slider.get_value()))
    cam_rotX_mat = pyrr.matrix44.create_from_x_rotation(np.deg2rad(camera_rotX_slider.get_value()))
    cam_rot_mat = pyrr.matrix44.multiply(cam_rotX_mat, cam_rotY_mat)
    rotated_eye = pyrr.matrix44.apply_to_vector(cam_rot_mat, eye)

    view_mat = pyrr.matrix44.create_look_at(rotated_eye, target, up)
    projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_slider.get_value(), aspect, near,  far)

    light_rotY = np.deg2rad(light_rotY_slider.get_value())
    rotated_lightPos = pyrr.matrix44.apply_to_vector(pyrr.matrix44.create_from_y_rotation(light_rotY), lightPos)

    render_scene()

    # Refresh the display to show what's been drawn
    pg.display.flip()



# Cleanup
glDeleteVertexArrays(2, [vao_obj])
glDeleteBuffers(2, [vbo_obj])

glDeleteProgram(shaderProgram_scene.shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program