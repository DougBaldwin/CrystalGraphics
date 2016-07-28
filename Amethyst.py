# This program is really a test/demonstration of modeling and rendering a simple
# crystal via a Python program that ultimately uses the Pyglet rendering library.
# This particular program, however, interacts with Pyglet through a "Renderer" class
# whose job is to abstract away from crystal models all the OpenGL mechanics provided
# by Pyglet.

# The image this program generates is a very simple amethyst (i.e., purple quartz)
# crystal consisting of a hexagonal prism with pyramidal ends. This habit comes from
# information at mindat.org (specifically its "quartz no. 7"), although it may not
# actually be a very common habit.

# Copyright 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from StaticScreenRenderer import StaticScreenRenderer
from math import pi, sin, cos




# Main program.


# Set up a renderer to draw the crystal.

renderer = StaticScreenRenderer()


# Report the version of any rendering engine or library that the renderer uses.

print "Renderer version:", renderer.version()


# Basic parameters of the crystal: a and c axis lengths, material properties, key c
# coordinates for prism and pyramid, etc.

a = 4.9133
c = 5.4053

material = ( 0.7, 0.1, 0.7, 0.5, 0.7, 20.0 )

topPrismC = 10
topPyramidC = topPrismC + c
bottomPrismC = -10
bottomPyramidC = bottomPrismC - c


# Generate the vertices for the triangles that make up the crystal.

topPyramidVertex = [ 0, topPyramidC, 0 ]
bottomPyramidVertex = [ 0, bottomPyramidC, 0 ]

topPrismVertices = []
bottomPrismVertices = []

theta = pi / 3						# Angle between a axes

for i in range( 6 ) :
    angle = i * theta
    x = a * sin( angle )
    z = a * cos( angle )
    topPrismVertices.append( [ x, topPrismC, z ] )
    bottomPrismVertices.append( [ x, bottomPrismC, z ] )


# Generate the triangles by stepping through angles around the prism. At each angle,
# generate a triangle from the top pyramid, two triangles forming a rectangular prism
# face, and a triangle from the bottom pyramid. Triangles generally run from the current
# angle to the next one.

for i in range( 6 ) :
	nextI = ( i + 1 ) % 6
	renderer.triangle( topPyramidVertex, topPrismVertices[i], topPrismVertices[nextI], material )
	renderer.triangle( topPrismVertices[i], bottomPrismVertices[i], topPrismVertices[nextI], material )
	renderer.triangle( topPrismVertices[nextI], bottomPrismVertices[i], bottomPrismVertices[nextI], material )
	renderer.triangle( bottomPrismVertices[i], bottomPyramidVertex, bottomPrismVertices[nextI], material )


# Draw the crystal.

renderer.viewer( 0.0, topPyramidC + c + 5.0, a + 22.0 )
renderer.draw()
