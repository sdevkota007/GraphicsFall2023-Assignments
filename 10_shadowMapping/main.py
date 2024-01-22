import pygame as pg
from OpenGL.GL import *
import numpy as np
import shaderLoaderV3
from objLoaderV4 import ObjLoader
from utils import load_image
from guiV3 import SimpleGUI
import pyrr

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
    # glBindAttribLocation(shader, position_loc, "position")
    # glBindAttribLocation(shader, tex_coord_loc, "uv")
    # glBindAttribLocation(shader, normal_loc, "normal")

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


def create_framebuffer_with_depth_attachment(width, height):
    # Create a framebuffer object
    framebuffer_id = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer_id)

    # Create a texture object for the depth attachment
    depthTex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, depthTex_id)

    # Define texture parameters
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, width, height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)  # Set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Attach the depth texture to the framebuffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthTex_id, 0)

    # Tell OpenGL which color attachments we'll use (of this framebuffer) for rendering.
    # We won't be using any color attachments so we can tell OpenGL that we're not going to bind any color attachments.
    # So set the draw and read buffer to none
    glDrawBuffer(GL_NONE)
    glReadBuffer(GL_NONE)

    # Check if framebuffer is complete
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise Exception("Framebuffer is not complete!")

    # Unbind the framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return framebuffer_id, depthTex_id




def render_scene():
    '''
    This function renders the scene from the camera's point of view.
    :return:
    '''
    # ***** Set Uniforms *****
    glUseProgram(shaderProgram_scene.shader)   # being explicit even though the line below will call this function
    shaderProgram_scene["viewMatrix"] = view_mat
    shaderProgram_scene["projectionMatrix"] = projection_mat

    shaderProgram_scene["materialColor"] = material_color_slider.get_color()
    shaderProgram_scene["lightPos"] = rotated_lightPos
    shaderProgram_scene["isPcf"] = isPcf_checkbox.get_value()
    shaderProgram_scene["nPCF"] = int(n_pcf_slider.get_value())

    shaderProgram_scene["lightViewMatrix"] = light_view_mat
    shaderProgram_scene["lightProjectionMatrix"] = light_projection_mat

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, depthTex_id)

    # ***** Draw object *****
    shaderProgram_scene["modelMatrix"] = model_mat_obj
    glBindVertexArray(vao_obj)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)
    # ***********************

    # ***** Draw receiver *****
    shaderProgram_scene["modelMatrix"] = model_mat_receiver
    glBindVertexArray(vao_receiver)
    glDrawArrays(GL_TRIANGLES, 0, obj_receiver.n_vertices)
    # ***********************



def render_tex():
    '''
    This function is optional. It is used to render the depth texture onto a quad for debugging purposes
    :return:
    '''
    glUseProgram(shaderProgram_visualizeTex.shader)  # being explicit even though the line below will call this function
    shaderProgram_visualizeTex["near"] = float(near)
    shaderProgram_visualizeTex["far"] = float(far)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, depthTex_id)

    glBindVertexArray(vao_receiver)
    glDrawArrays(GL_TRIANGLES, 0, obj_receiver.n_vertices)


def render_shadow_map():
    '''
    This function renders the scene from the light's point of view and stores the depth of each point in the scene
    in a texture.
    Since we don't want to render the color of the scene, we will use a custom framebuffer with a depth attachment and
    no color attachments. This depth buffer (which is also called shadow map) will be used as a texture in the next part.
    Since there is no color attachment, we won't be able to see anything on the screen.

    :return:
    '''
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer_id)
    glClear(GL_DEPTH_BUFFER_BIT)

    # ***** render the object and receiver *****
    glUseProgram(shaderProgram_shadowMap.shader)  # being explicit even though the line below will call this function

    shaderProgram_shadowMap["viewMatrix"] = light_view_mat
    shaderProgram_shadowMap["projectionMatrix"] = light_projection_mat

    # ***** Draw object *****
    shaderProgram_shadowMap["modelMatrix"] = model_mat_obj
    glBindVertexArray(vao_obj)
    glDrawArrays(GL_TRIANGLES, 0, obj.n_vertices)  # Draw the triangle

    # ***** Draw receiver *****
    shaderProgram_shadowMap["modelMatrix"] = model_mat_receiver
    glBindVertexArray(vao_receiver)
    glDrawArrays(GL_TRIANGLES, 0, obj_receiver.n_vertices)  # Draw the triangle

    glBindFramebuffer(GL_FRAMEBUFFER, 0)




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
# Shader to generate the depth texture (shadown map) from light's point of view
shaderProgram_shadowMap = shaderLoaderV3.ShaderProgram("shaders/shadowMap/vert_shadowMap.glsl", "shaders/shadowMap/frag_shadowMap.glsl")
# optional: to render the depth texture onto a quad. Only used for debugging purposes
shaderProgram_visualizeTex = shaderLoaderV3.ShaderProgram("shaders/visualizeDepthTex/vert_tex.glsl", "shaders/visualizeDepthTex/frag_tex.glsl")
# Shader to render the scene with shadow from camera's point of view
shaderProgram_scene = shaderLoaderV3.ShaderProgram("shaders/scene/vert_scene.glsl", "shaders/scene/frag_scene.glsl")


'''
# **************************************************************************************************************
# Load our objects and configure their attributes
# **************************************************************************************************************
'''
# obj = ObjLoader("objects/rayman/raymanModel.obj")
obj = ObjLoader("objects/teapot.obj")
vao_obj, vbo_obj, n_vertices_obj = upload_and_configure_attributes(obj, shaderProgram_scene.shader)

obj_receiver = ObjLoader("objects/square.obj")
vao_receiver, vbo_receiver, n_vertices_receiver = upload_and_configure_attributes(obj_receiver, shaderProgram_scene.shader)

# **************************************************************************************************************
# **************************************************************************************************************



'''
# **************************************************************************************************************
# Define camera attributes
# **************************************************************************************************************
'''
eye = (0,3,4)
target = (0,0,0)
up = (0,1,0)

fov = 45
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

# for receiver
rotation_mat = pyrr.matrix44.create_from_x_rotation(np.deg2rad(90))
translation_mat = pyrr.matrix44.create_from_translation([0, -1, 0])
scaling_mat = pyrr.matrix44.create_from_scale([2, 2, 2])
model_mat_receiver = pyrr.matrix44.multiply(scaling_mat, rotation_mat)
model_mat_receiver = pyrr.matrix44.multiply(model_mat_receiver, translation_mat)
# **************************************************************************************************************
# **************************************************************************************************************




'''
# **************************************************************************************************************
# Framebuffer
# **************************************************************************************************************
'''
framebuffer_id, depthTex_id = create_framebuffer_with_depth_attachment(width, height)
shaderProgram_scene["depthTex"] = 0
shaderProgram_visualizeTex["depthTex"] = 0


'''
# **************************************************************************************************************
# Setup gui
# **************************************************************************************************************
'''
gui = SimpleGUI("Skybox")

# Create a slider for the rotation angle around the Y axis
light_rotY_slider = gui.add_slider("light Y angle", -180, 180, 0, resolution=1)

camera_rotY_slider = gui.add_slider("camera Y angle", -180, 180, 0, resolution=1)
camera_rotX_slider = gui.add_slider("camera X angle", -90, 90, 0, resolution=1)
fov_slider = gui.add_slider("fov", fov, 120, fov, resolution=1)

material_color_slider = gui.add_color_picker(label_text="Material Color", initial_color=(0.8, 0.8, 0.8))
render_type_radio = gui.add_radio_buttons(label_text="Render Type",
                                          options_dict={"Depth (Light's POV)": 0,"Scene with shadow": 1,},
                                          initial_option="Scene with shadow")

isPcf_checkbox = gui.add_checkbox("PCF", True)
n_pcf_slider = gui.add_slider("nPCF", min_value=0, max_value=8, initial_value=1, resolution=1)

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

    # view and projection matrices from the light's point of view
    light_rotY_mat = pyrr.matrix44.create_from_y_rotation(np.deg2rad(light_rotY_slider.get_value()))
    rotated_lightPos = pyrr.matrix44.apply_to_vector(light_rotY_mat, lightPos)

    light_view_mat = pyrr.matrix44.create_look_at(rotated_lightPos, target, up)
    light_projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_slider.get_value(), aspect, near, far)

    # render the shadow map
    render_shadow_map()

    if(int(render_type_radio.get_value()) == 0):
        render_tex()        # optional: render the depth texture onto a quad for debugging purposes
    else:
        render_scene()      # render the scene with shadow. You need to implement this function

    # Refresh the display to show what's been drawn
    pg.display.flip()



# Cleanup
glDeleteVertexArrays(2, [vao_obj, vao_receiver])
glDeleteBuffers(2, [vbo_obj, vao_receiver])

glDeleteProgram(shaderProgram_scene.shader)
glDeleteProgram(shaderProgram_shadowMap.shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program