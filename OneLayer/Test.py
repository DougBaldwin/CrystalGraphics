# A test program for parts of my single-layer crystal aggregate project. The
# idea is for this to be a driver I can change however I want in order to do
# small, tightly controlled tests on other parts of the project.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2022. Created by Doug Baldwin from the actual driver for the project.


from Amethyst import Amethyst
from Substrate import Substrate
from Vertex import Vertex
from Polyhedron import Polyhedron
from RotatingScreenRenderer import RotatingScreenRenderer




# Create a renderer for drawing test results.

renderer = RotatingScreenRenderer( 3.0, 3.5 )


# The current test is 2 interpenetrating amethysts on a subtrate, that
# hopefully show certain faces not being completely clipped.

substrateMinX = -1.0
substrateMaxX = 1.0
substrateMaxY = 0.5
substrateMinZ = -1.0
substrateMaxZ = 1.0

base = Substrate( substrateMinX, substrateMaxX, 0.0, substrateMaxY, substrateMinZ, substrateMaxZ )

base.draw( renderer )


vertices1 = [ Vertex(-0.9, 0.7, 0.),
			  Vertex(-0.9, 0.7, 0.5),
			  Vertex(-1.05, 0.0, 0.0),
			  Vertex(-1.05, 0.0, 0.5),
			  Vertex(0.6, 0.7, 0.0),
			  Vertex(0.6, 0.7, 0.5),
			  Vertex(0.45, 0.0, 0.0),
			  Vertex(0.45, 0.0, 0.5) ]

color1 = ( 0.53, 0.38, 0.93, 0.55, 0.85, 50.0 )

vertices2 = [ Vertex(-0.2, 1.0, 0.2),
			  Vertex(-0.2, 1.0, 0.8),
			  Vertex(-0.2, 0.2, 0.2),
			  Vertex(-0.2, 0.2, 0.8),
			  Vertex(0.2, 1.0, 0.2),
			  Vertex(0.2, 1.0, 0.8),
			  Vertex(0.2, 0.2, 0.2),
			  Vertex(0.2, 0.2, 0.8) ]

color2 = (0.83, 0.68, 0.33, 0.55, 0.85, 50.0)

rectangleFaces = [ [0, 2, 3, 1],
				   [1, 3, 7, 5],
				   [4, 5, 7, 6],
				   [0, 4, 6, 2],
				   [2, 6, 7, 3],
				   [0, 1, 5, 4] ]

a1 = Polyhedron( vertices1, rectangleFaces, color1 )
a1.clipTo( base )
a1.draw( renderer )

a2 = Polyhedron( vertices2, rectangleFaces, color2 )
a2.clipTo( base )
a2.clipTo( a1 )
a2.draw( renderer )


# Draw the test shape.

renderer.draw()
