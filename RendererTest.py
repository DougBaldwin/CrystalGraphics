# This program is a set of artificial tests of a Python "renderer" class that is supposed
# to hide the complexity of drawing crystals and crystal aggregates with Pyglet. The
# program simply draws a handful of triangles and views them in simple ways intended to
# make it easy to tell whether the renderer is doing what it should, and if not, to figure
# out why. Different functions set up different "handsful of triangles," so by changing
# one function call in the main program I can change the exact test I do.

# Copyright (C) 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)




# The various test functions. Each of these takes a renderer as its only argument, and
# adds some triangles to that renderer. The triangles should all have z coordinates
# between -1 and 1, fitting into a frustum that extends 1/2 a unit from (0,0) at the
# closest point to the viewer and 3/2 of a unit at the furthest point from the viewer.


# Three triangles, two that together display upward-angled sides when rendered in
# perspective, and a third dark triangle showing through from behind them.

def translucency( renderer ) :

	leftColor = [ 1.0, 0.0, 0.0, 0.3, 0.5, 1.0 ]
	rightColor = [ 0.0, 0.0, 1.0, 0.3, 0.5, 1.0 ]
	backColor = [ 0.0, 0.7, 0.0, 1.0, 0.5, 1.0 ]

	bottomCenter = [ 0.0, -0.5, 0.0 ]
	topCenter = [ 0.0, 0.5, 0.0 ]
	leftCorner = [ -0.5, -0.5, -0.75 ]
	rightCorner = [ 0.5, -0.5, -0.75 ]
	backTopLeft = [ -0.7, 0.3, -0.8 ]
	backBottomLeft = [ -0.7, -0.3, -0.8 ]
	backRight = [ 0.7, 0.0, -0.8 ]

	renderer.triangle( backBottomLeft, backRight, backTopLeft, backColor )
	renderer.triangle( bottomCenter, topCenter, leftCorner, leftColor )
	renderer.triangle( bottomCenter, rightCorner, topCenter, rightColor )


# Two triangles, that between them should just fill the viewport.

def viewportSize( renderer ) :
	
	lowLeftColor = [ 1.0, 0.0, 0.0, 1.0, 0.0, 1.0 ]
	highRightColor = [ 0.0, 0.0, 1.0, 1.0, 0.0, 1.0 ]
	
	lowLeft = [ -0.5, -0.5, 0.99 ]
	lowRight = [ 0.5, -0.5, 0.99 ]
	highLeft = [ -0.5, 0.5, 0.99 ]
	highRight = [ 0.5, 0.5, 0.99 ]
	
	renderer.triangle( lowLeft, lowRight, highLeft, lowLeftColor )
	renderer.triangle( highLeft, lowRight, highRight, highRightColor )




# The main program. This creates a renderer and calls one or more of the test functions
# to populate it with triangles. It then ends by putting a viewer at (0,0,2) and drawing
# the triangles.

from StaticScreenRenderer import StaticScreenRenderer
renderer = StaticScreenRenderer()

viewportSize( renderer )

renderer.viewer( 0.0, 0.0, 2.0 )
renderer.draw()
