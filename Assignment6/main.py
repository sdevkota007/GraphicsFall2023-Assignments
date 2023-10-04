# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

from guiV1 import SimpleGUI
from objLoaderV4 import ObjLoader
import shaderLoader
import pyrr


# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 640
height = 480
pg.display.set_mode((width *2, height), pg.OPENGL | pg.DOUBLEBUF)


# glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_SCISSOR_TEST)



# Write our shaders. We will write our vertex shader and fragment shader in a different file
shader1 = shaderLoader.compile_shader("shaders/obj1/vert.glsl", "shaders/obj1/frag.glsl")
shader2 = shaderLoader.compile_shader("shaders/obj2/vert.glsl", "shaders/obj2/frag.glsl")


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
# *************************************************************************


# Lets load our objects
obj1 = ObjLoader("objects/raymanModel.obj")
obj2 = ObjLoader("objects/dragon.obj")


# *********** Lets define model matrix for object 1 ***********
translation_mat = pyrr.matrix44.create_from_translation(-obj1.center)
scaling_mat = pyrr.matrix44.create_from_scale([2/obj1.dia, 2/obj1.dia, 2/obj1.dia])
model_mat1 = pyrr.matrix44.multiply(translation_mat, scaling_mat)

# *********** Lets define model matrix for object 2 ***********
translation_mat = pyrr.matrix44.create_from_translation(-obj2.center)
scaling_mat = pyrr.matrix44.create_from_scale([2/obj2.dia, 2/obj2.dia, 2/obj2.dia])
model_mat2 = pyrr.matrix44.multiply(translation_mat, scaling_mat)


# ***** Create VAO, VBO, and configure vertex attributes for object 1 *****
# VAO
vao1 = glGenVertexArrays(1)
glBindVertexArray(vao1)

# VBO
vbo1 = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo1)
glBufferData(GL_ARRAY_BUFFER, obj1.vertices.nbytes, obj1.vertices, GL_STATIC_DRAW)

# Configure vertex attributes for object 1
position_loc = glGetAttribLocation(shader1, "position")
glVertexAttribPointer(position_loc, obj1.size_position, GL_FLOAT, GL_FALSE, obj1.stride, ctypes.c_void_p(obj1.offset_position))
glEnableVertexAttribArray(position_loc)

normal_loc = glGetAttribLocation(shader1, "normal")
glVertexAttribPointer(normal_loc, obj1.size_normal, GL_FLOAT, GL_FALSE, obj1.stride, ctypes.c_void_p(obj1.offset_normal))
glEnableVertexAttribArray(normal_loc)
# *************************************************************************



# ***** Create VAO, VBO, and configure vertex attributes for object 2 *****
# VAO
vao2 = glGenVertexArrays(1)
glBindVertexArray(vao2)
# VBO
vbo2 = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo2)
glBufferData(GL_ARRAY_BUFFER, obj2.vertices.nbytes, obj2.vertices, GL_STATIC_DRAW)

# Configure vertex attributes for object 1
position_loc = glGetAttribLocation(shader2, "position")
glVertexAttribPointer(position_loc, obj2.size_position, GL_FLOAT, GL_FALSE, obj2.stride, ctypes.c_void_p(obj2.offset_position))
glEnableVertexAttribArray(position_loc)

normal_loc = glGetAttribLocation(shader2, "normal")
glVertexAttribPointer(normal_loc, obj2.size_normal, GL_FLOAT, GL_FALSE, obj2.stride, ctypes.c_void_p(obj2.offset_normal))
glEnableVertexAttribArray(normal_loc)
# *************************************************************************




gui = SimpleGUI("Assignment 6")

# Create a slider for the rotation angle around the Z axis
camera_rotY_slider = gui.add_slider("camera Y angle", -180, 180, 0)
camera_rotX_slider = gui.add_slider("camera X angle", -90, 90, 0)
fov_slider = gui.add_slider("fov", 25, 90, 45)


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


    # ****************************************** Draw Object 1 ******************************************
    glViewport(0, 0, width, height)
    glScissor(0, 0, width, height)
    glClearColor(0.3, 0.4, 0.5, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Use the shader1 and configure the uniforms for shader1
    glUseProgram(shader1)
    glUniformMatrix4fv(glGetUniformLocation(shader1, "model_matrix"),1,
                       GL_FALSE,
                       model_mat1)
    glUniformMatrix4fv(glGetUniformLocation(shader1, "view_matrix"),1,
                       GL_FALSE,
                       view_mat)
    glUniformMatrix4fv(glGetUniformLocation(shader1, "projection_matrix"),1,
                       GL_FALSE,
                       projection_mat)
    # bind the VAO for object 1
    glBindVertexArray(vao1)
    glDrawArrays(GL_TRIANGLES,0, obj1.n_vertices)      # Finally draw the object
    # ****************************************************************************************************


    # ****************************************** Draw Object 2 ******************************************
    glViewport(width, 0, width, height)
    glScissor(width, 0, width, height)
    glClearColor(0.2, 0.3, 0.4, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    # Use the shader2 and configure the uniforms for shader2
    glUseProgram(shader2)
    glUniformMatrix4fv(glGetUniformLocation(shader2, "model_matrix"),1,
                       GL_FALSE,
                       model_mat2)
    glUniformMatrix4fv(glGetUniformLocation(shader2, "view_matrix"),1,
                       GL_FALSE,
                       view_mat)
    glUniformMatrix4fv(glGetUniformLocation(shader2, "projection_matrix"),1,
                       GL_FALSE,
                       projection_mat)
    # bind the VAO for object 2
    glBindVertexArray(vao2)
    glDrawArrays(GL_TRIANGLES,0, obj2.n_vertices)      # Finally draw the object
    # ****************************************************************************************************


    # Refresh the display to show what's been drawn
    pg.display.flip()


# Cleanup
glDeleteVertexArrays(1, [vao1, vao2])
glDeleteBuffers(1, [vbo1, vbo2])
glDeleteProgram(shader1)
glDeleteProgram(shader2)

pg.quit()   # Close the graphics window
quit()      # Exit the program