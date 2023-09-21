# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np

# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 640
height = 480
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)

# Todo: Part 1
# Set the background color (clear color)
# glClearColor takes 4 arguments: red, green, blue, alpha. Each argument is a float between 0 and 1.
glClearColor(0.3, 0.4, 0.5, 1.0)



# Todo: Part 2

from objLoaderV1 import ObjLoader
obj = ObjLoader("objects/raymanModel.obj")
positions = obj.v
print("Dimension of v: ", obj.v.shape)
print("Dimension of vt: ", obj.vt.shape)
print("Dimension of vn: ", obj.vn.shape)
print("Dimension of vertices: ", obj.vertices.shape)



# Todo: Part 3

min = np.array([np.inf, np.inf, np.inf])
max = np.array([-np.inf, -np.inf, -np.inf])

for arr in positions:
    arr = np.array(arr)
    min = np.minimum(min, arr)
    max = np.maximum(max, arr)

dia = np.linalg.norm(max - min)
center = (min + max) / 2

print("Min: ", min)
print("Max: ", max)
print("Center: ", center)
print("Diameter: ", dia)




# Todo: Part 4
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)


# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear the screen (or clear the color buffer), and set it to the background color chosen earlier
    glClear(GL_COLOR_BUFFER_BIT)

    # Refresh the display to show what's been drawn
    pg.display.flip()


pg.quit()   # Close the graphics window
quit()      # Exit the program