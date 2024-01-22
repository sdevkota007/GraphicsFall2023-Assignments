# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from guiV2 import SimpleGUI
from objLoaderV4 import ObjLoader
import shaderLoaderV3
import pyrr


# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 1024
height = 768
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)


# Write our shaders. We will write our vertex shader and fragment shader in a different file
shaderProgram = shaderLoaderV3.ShaderProgram("shaders/vert.glsl", "shaders/frag.glsl")

# Camera parameters
eye = (0,0,2.5)
target = (0,0,0)
up = (0,1,0)

fov = 60
aspect = width/height
near = 0.1
far = 10

view_mat  = pyrr.matrix44.create_look_at(eye, target, up)
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)

# light and material properties
material_color = (1.0, 0.1, 0.1)
light_pos = np.array([2, 2, 2, None], dtype=np.float32)     # last component is for light type (0: directional, 1: point) which is changed by radio button
ambient_intensity = 0.25
specular_color = (1, 1, 1)
shininess = 32
K_s = 0.5

LEFT = -1
MIDDLE = 0
RIGHT = 1

# *************************************************************************


# Lets load our objects
obj = ObjLoader("objects/dragon.obj")



# *********** Lets define model matrix ***********
translation_left_mat = pyrr.matrix44.create_from_translation(-obj.center - [obj.dia/2, 0, 0])
translation_mat = pyrr.matrix44.create_from_translation(-obj.center)
translation_right_mat = pyrr.matrix44.create_from_translation(-obj.center + [obj.dia/2, 0, 0])

scaling_mat = pyrr.matrix44.create_from_scale([2 / obj.dia, 2 / obj.dia, 2 / obj.dia])

model_left_mat = pyrr.matrix44.multiply(translation_left_mat, scaling_mat)
model_mat = pyrr.matrix44.multiply(translation_mat, scaling_mat)
model_right_mat = pyrr.matrix44.multiply(translation_right_mat, scaling_mat)


# translation_right_mat = pyrr.matrix44.create_from_translation([1.5*RIGHT, 0, 0])
# model_right_mat = pyrr.matrix44.multiply(model_mat, translation_right_mat)


# ***** Create VAO, VBO, and configure vertex attributes for object 1 *****
# VAO
vao = glGenVertexArrays(1)
glBindVertexArray(vao)

# VBO
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)

# Configure vertex attributes for object 1
position_loc = 0
glVertexAttribPointer(position_loc, obj.size_position, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_position))
glEnableVertexAttribArray(position_loc)

normal_loc = 1
glVertexAttribPointer(normal_loc, obj.size_normal, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_normal))
glEnableVertexAttribArray(normal_loc)
# *************************************************************************





gui = SimpleGUI("Assignment 7")

# Create a slider for the rotation angle around the Z axis
camera_rotY_slider = gui.add_slider("camera Y angle", -180, 180, 0, resolution=1)
camera_rotX_slider = gui.add_slider("camera X angle", -90, 90, 0, resolution=1)
fov_slider = gui.add_slider("fov", 25, 90, fov, resolution=1)

shininess_slider = gui.add_slider("shininess", 1, 128, 32, resolution=1)
K_s_slider = gui.add_slider("K_s", 0, 1, 0.5)

material_color_picker = gui.add_color_picker("material color", initial_color=material_color)
specular_color_picker = gui.add_color_picker("specular color", initial_color=specular_color)
light_type_radio_button = gui.add_radio_buttons("light type", options_dict={"point":1, "directional":0}, initial_option="point")

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

    light_pos[3] = light_type_radio_button.get_value()

    # Set uniforms
    shaderProgram["model_matrix"] = model_mat
    shaderProgram["object_id"] = MIDDLE
    shaderProgram["view_matrix"] = view_mat
    shaderProgram["projection_matrix"] = projection_mat
    shaderProgram["eye_pos"] = rotated_eye
    shaderProgram["material_color"] = material_color_picker.get_color()
    shaderProgram["specular_color"] = specular_color_picker.get_color()
    shaderProgram["shininess"] = shininess_slider.get_value()
    shaderProgram["K_s"] = K_s_slider.get_value()
    shaderProgram["light_pos"] = light_pos
    shaderProgram["ambient_intensity"] = ambient_intensity



    # set uniforms and draw object in the left
    shaderProgram["model_matrix"] = model_left_mat
    shaderProgram["object_id"] = LEFT

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)      # Finally draw the object
    # ****************************************************************************************************

    # set uniforms and draw object in the middle
    shaderProgram["model_matrix"] = model_mat
    shaderProgram["object_id"] = MIDDLE

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)      # Finally draw the object
    # ****************************************************************************************************


    # set uniforms and draw object in the right
    shaderProgram["model_matrix"] = model_right_mat
    shaderProgram["object_id"] = RIGHT

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)      # Finally draw the object
    # ****************************************************************************************************


    # Refresh the display to show what's been drawn
    pg.display.flip()


# Cleanup
glDeleteVertexArrays(1, [vao])
glDeleteBuffers(1, [vbo])
glDeleteProgram(shaderProgram.shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program