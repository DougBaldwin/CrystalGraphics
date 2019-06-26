# This program is one of several tests for an animated screen renderer, i.e., an
# object that knows how to draw scenes that change with time. See file
# "AnimatedScreenRenderer.py" for more information about that renderer. This program
# exercises the renderer by drawing a set of triangles that grows over time. New triangles
# enter the scene at a rate of a couple per second. Once added to the scene triangles
# don't change, but the total number of them is always increasing. Each triangle is a
# right triangle whose apex is randomly positioned in the 2-by-2-by-2 cube centered at
# the origin.

# Copyright (C) 2016 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)

# History:
#
#   June  2019 -- Created by Doug Baldwin.


from AnimatedScreenRenderer import AnimatedScreenRenderer
from random import uniform, randrange




# The triangles this program draws come from a list that gradually increases in size. Each
# triangle in the list is represented by a 6-tuple, containing the triangle's x, y, and z
# coordinates, and its red, green, and blue color components, in that order. The list of
# triangles starts out empty.

triangles = []




# Create a triangle and add it to the list of triangles that form the scene to draw.
# Give the triangle a random position and color.

def makeTriangle() :
	
	
	# Generate random x, y, and z coordinates for this triangle.
	
	x = uniform( -1.0, 1.0 )
	y = uniform( -1.0, 1.0 )
	z = uniform( -1.0, 1.0 )
	
	
	# Generate random RGB color components for this triangle.
	
	r = uniform( 0.0, 1.0 )
	g = uniform( 0.0, 1.0 )
	b = uniform( 0.0, 1.0 )
	
	
	# Add the triangle to the list of triangles that will get drawn.
	
	global triangles
	
	triangles.append( ( x, y, z, r, g, b ) )




# Possibly add a triangle to the scene, and then draw all triangles to a given renderer.
# Ignore the second argument, the time since the last animation step.

def drawTriangles( renderer, dt ) :
	
	
	# Randomly decide whether to add a new triangle, with odds of roughly 1 in 20 that
	# I will. Based on a more or less 30 frames per second animation rate, this should
	# produce 1 or 2 new triangles each second.
	
	if randrange(20) == 0 :
		makeTriangle()	
	
	
	# Draw the triangles.
	
	global triangles
	for t in triangles :
	
		v1 = [ t[0], t[1], t[2] ]				# Apex
		v2 = [ t[0] + 0.2, t[1], t[2] ]
		v3 = [ t[0], t[1] + 0.2, t[2] ]
		color = [ t[3], t[4], t[5], 1.0, 0.1, 1.0 ]
		
		renderer.triangle( v1, v2, v3, color )
		





# Main program.


# Set up the renderer.

renderer = AnimatedScreenRenderer( drawTriangles, None )
renderer.viewer( 0.0, 1.5, 4.0 )


# Start the scene with one triangle.

makeTriangle()


# Draw the scene.

renderer.draw()
