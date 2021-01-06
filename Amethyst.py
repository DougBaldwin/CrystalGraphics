# This program is really a test/demonstration of modeling and rendering a simple crystal
# via Python. The program can display the crystal in several ways, depending on which of
# several "renderer" objects it uses for final rendering. Users indicate which renderer
# they want via the "-r" command-line option:
#   -r rotate - Use a renderer that animates the viewer orbitting around the crystal (or
#               the crystal rotating beneath the viewer). Default choice.
#   -r static - Use a renderer that draws a static image of the crystal
#   -r 3d     - Use a renderer that produces an "STL" file for a 3D printer.
# So the usage of this program is as in
#   amethyst.py -r <renderer>

# The image this program generates is a very simple amethyst (i.e., purple quartz)
# crystal consisting of a hexagonal prism with pyramidal ends. This habit comes from
# information at mindat.org (specifically its "quartz no. 7"), although it may not
# actually be a very common habit.

# Copyright 2016 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from StaticScreenRenderer import StaticScreenRenderer
from RotatingScreenRenderer import RotatingScreenRenderer
from STLRenderer import ASCIISTLRenderer
from math import pi, sin, cos, sqrt
from argparse import ArgumentParser
import sys




# Main program.


# Basic parameters of the crystal: a and c axis lengths, material properties, key
# coordinates for prism and pyramid, etc.

a = 4.9133
c = 5.4053

material = ( 0.58, 0.3, 0.8, 0.58, 0.85, 50.0 )

topPrismC = 10
topPyramidC = topPrismC + c
bottomPrismC = -10
bottomPyramidC = bottomPrismC - c


# Based on the user's request, create the appropriate renderer to draw the crystal.

parser = ArgumentParser()
parser.add_argument( "-r", action="store", default="rotate", choices=["rotate","static","3d"],
					 help="Specify rendering to a rotating view, static view, or 3d printer file" )

arguments = parser.parse_args()

viewerX = 0.0							# Initial x coordinate for viewer
viewerY = topPyramidC + c + 5.0			# Initial viewer y coordinate
viewerZ = a + 22.0						# Initial z

if arguments.r == "rotate" :
	renderer = RotatingScreenRenderer( viewerY, sqrt( viewerY**2 + viewerZ**2 ) )

elif arguments.r == "static" :
	renderer =  StaticScreenRenderer()
	renderer.viewer( viewerX, viewerY, viewerZ )

elif arguments.r == "3d" :
	renderer = ASCIISTLRenderer( "amethyst.stl" )

else :
	print( "Renderer '" + arguments.r + "' must be one of 'rotate', 'static', or '3d'" )
	sys.exit( 1 )


# Report the version of any rendering engine or library that the renderer uses.

print( "Renderer version:", renderer.version() )


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

renderer.draw()
