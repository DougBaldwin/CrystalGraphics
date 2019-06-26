# This program is one of several tests for an animated screen renderer, i.e., an
# object that knows how to draw scenes that change with time. See file
# "AnimatedScreenRenderer.py" for more information about that renderer. This program
# exercises the renderer by drawing a cylinder that expands over time. This means that
# the total number of triangles in the scene doesn't change, although the vertices of
# each triangle do.

# Copyright (C) 2016 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)

# History:
#
#   June  2019 -- Created by Doug Baldwin.


from AnimatedScreenRenderer import AnimatedScreenRenderer
from math import sin, cos, pi




# A function that "grows" the cylinder by one time step, drawing the resulting triangles
# to a given renderer. The second argument to this function, the time since the last step,
# is ignored.

# The cylinder is aligned with the y axis, centered at the origin. I thus define it
# by its extent above or below the origin in the y direction, and its radius. At
# each time step, these things change by a specified delta. The extent and radius are
# initially 0, and will then increase at the beginning of each step.

extent = 0.0
radius = 0.0

dExtent = 0.01
dRadius = 0.01 


def growCylinder( renderer, dt ) :
	
	
	# Grow the cylinder's radius and extent.
	
	global extent, radius
	
	extent += dExtent
	radius += dRadius 
	
	
	# Generate vertices around the top and bottom of the cylinder.
	
	topVertices = []
	bottomVertices = []
	
	nVertices = 20
	dAngle = 2 * pi / nVertices
	
	for v in range( nVertices ) :
	
		angle = v * dAngle
		x = radius * cos( angle )
		z = radius * sin( angle )
		
		topVertices.append( [ x, extent, z ] )
		bottomVertices.append( [ x, -extent, z ] )
	
	
	# Create triangles connecting the center of the top to the cylinder to the upper
	# vertices, the upper vertices to the lower, and the lower to the center of the
	# bottom of the cylinder, and add all  these triangles to the renderer.
	
	topCenter = [ 0.0, extent, 0.0 ]
	bottomCenter = [ 0.0, -extent, 0.0 ]
	
	sideColor = [ 0.9, 0.1, 0.1, 1.0, 0.4, 10.0 ]
	topColor = [ 0.3, 0.4, 0.8, 1.0, 0.1, 1.0 ]
	bottomColor = [ 0.1, 0.8, 0.1, 1.0, 0.4, 10.0 ]
	
	for v in range( nVertices ) :
	
		next = ( v + 1 ) % nVertices
		
		renderer.triangle( topCenter, topVertices[next], topVertices[v], topColor )
		renderer.triangle( topVertices[v], bottomVertices[next], bottomVertices[v], sideColor )
		renderer.triangle( topVertices[next], bottomVertices[next], topVertices[v], sideColor )
		renderer.triangle( bottomCenter, bottomVertices[v], bottomVertices[next], bottomColor )
	
	
	# Create one last set of triangles, connecting the last vertices listed back to the
	# first.
	
	renderer.triangle( topCenter, topVertices[0], topVertices[nVertices-1], topColor )
	renderer.triangle( topVertices[nVertices-1], bottomVertices[0], bottomVertices[nVertices-1], sideColor )
	renderer.triangle( topVertices[0], bottomVertices[0], topVertices[nVertices-1], sideColor )
	renderer.triangle( bottomCenter, bottomVertices[nVertices-1], bottomVertices[0], bottomColor )
	





# The main program.

# Create the renderer.

renderer = AnimatedScreenRenderer( growCylinder, None )
renderer.viewer( 5.0, 5.0, 0.0 )


# Give it an initial cylinder.

growCylinder( renderer, 0 )


# Draw the cylinder.

renderer.draw()
