# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from guiV3 import SimpleGUI
from objLoaderV4 import ObjLoader
import shaderLoaderV3
import pyrr


# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 900
height = 500
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)


# Write our shaders. We will write our vertex shader and fragment shader in a different file
shaderProgram = shaderLoaderV3.ShaderProgram("shaders/vert.glsl", "shaders/frag.glsl")

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


# light and material properties
light_pos = np.array([2, 2, 2, None], dtype=np.float32)
material_color = (1.0, 0.1, 0.1)
# *************************************************************************


# Lets load our objects
obj = ObjLoader("../objects/teapot.obj")



# *********** Lets define model matrix ***********
translation_mat = pyrr.matrix44.create_from_translation(-obj.center)
scaling_mat = pyrr.matrix44.create_from_scale([2 / obj.dia, 2 / obj.dia, 2 / obj.dia])
model_mat = pyrr.matrix44.multiply(translation_mat, scaling_mat)


# ***** Create VAO, VBO, and configure vertex attributes for object 1 *****
# VAO
vao = glGenVertexArrays(1)
glBindVertexArray(vao)

# VBO
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)

# Configure vertex attributes for object 1
position_loc = glGetAttribLocation(shaderProgram.shader, "position")
glVertexAttribPointer(position_loc, obj.size_position, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_position))
glEnableVertexAttribArray(position_loc)

normal_loc = glGetAttribLocation(shaderProgram.shader, "normal")
glVertexAttribPointer(normal_loc, obj.size_normal, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_normal))
glEnableVertexAttribArray(normal_loc)
# *************************************************************************



gui = SimpleGUI("Assignment 7")

# Create a slider for the rotation angle around the Z axis
camera_rotY_slider = gui.add_slider("camera Y angle", -180, 180, 0, resolution=1)
camera_rotX_slider = gui.add_slider("camera X angle", -90, 90, 0, resolution=1)
fov_slider = gui.add_slider("fov", 25, 90, 45, resolution=1)


material_color_picker = gui.add_color_picker("material color", initial_color=material_color)

light_type_radio_button = gui.add_radio_buttons("light type", options_dict={"point":1, "directional":0}, initial_option="point")

shading_mode_radio_button = gui.add_radio_buttons("Shading type", options_dict={"Diffuse":0, "Toon shading":1}, initial_option="Toon shading")
isSilhouette_checkbox = gui.add_checkbox("Silhouette", initial_state=False)
isSmooth_checkbox = gui.add_checkbox("Smooth shading", initial_state=False)



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

    # Set uniforms
    shaderProgram["model_matrix"] = model_mat
    shaderProgram["view_matrix"] = view_mat
    shaderProgram["projection_matrix"] = projection_mat

    shaderProgram["shading_mode"] = int(shading_mode_radio_button.get_value())
    shaderProgram["isSmooth"] = isSmooth_checkbox.get_value()
    shaderProgram["isSilhouette"] = isSilhouette_checkbox.get_value()

    light_pos[3] = light_type_radio_button.get_value()

    shaderProgram["eye_pos"] = rotated_eye
    shaderProgram["material_color"] = material_color_picker.get_color()
    shaderProgram["light_pos"] = light_pos

    glUseProgram(shaderProgram.shader)

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)      # draw the object
    # ****************************************************************************************************


    # Refresh the display to show what's been drawn
    pg.display.flip()


# Cleanup
glDeleteVertexArrays(1, [vao])
glDeleteBuffers(1, [vbo])
glDeleteProgram(shaderProgram.shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program