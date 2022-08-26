# A class that represents amethyst crystals from which to make an aggregate.
# These crystals have the common hexagonal-prism-with-pyramid ends form for
# amethyst.
#
# This class is part of my experiment with generating visually realistic
# aggregates by taking crystal sizes from an appropriate probability
# distribution. See the project notes for more information on this effort.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.


from Polyhedron import Polyhedron
from Vertex import Vertex
from VectorOps import matrixMultiply
from math import sin, cos, pi




class Amethyst ( Polyhedron ) :
	
	
	
	
	# Initialize an amethyst, given its center point, a polar angle between the
	# y axis and its c axis, the angle between its c axis and the positive x
	# axis (specifically, the angle in the direction from the x axis towards
	# the z axis), and the distance the c axis extends either side of the
	# center, not counting the pyramids at the ends of the crystal.
	
	def __init__( self, position, polar, azimuth, size ) :


		# The basic strategy for initializing an amethyst is to transform
		# vertices in a canonical coordinate frame whose origin is at the
		# center of the crystal and whose crystallographic c axis is aligned
		# with the positive y coordinate system axis, and crystallographic a1
		# axis with x, into vertices in the global coordinate system. See the
		# July 3, 2019 project notes for some helpful geometry for canonical
		# crystals. The transformation involves rotating the canonical
		# coordinates through the polar angle and then the azimuth angle to
		# orient the crystals correctly, then finally translating them to their
		# proper locations.

		aSize = 0.9 * size				# Crystal's extent in the a dimensions
		hexAngle = pi / 3.0				# Radian measure of 60 degree angle between faces of hexagon


		# List the vertices of the canonical crystal. Each vertex is a column
		# vector in homogeneous coordinates, as my utility functions understand
		# such things, so I can easily change its coordinate system by matrix
		# multiplication.

		canonicalVertices = [[[0.0], [size + 1.1 * aSize], [0.0], [1.0]],							# 0: Apex of top pyramid
							 [[aSize], [size], [0.0], [1.0]],										# 1: Start of top of hexagonal body
							 [[aSize * cos(hexAngle)], [size], [aSize * sin(hexAngle)], [1.0]],
							 [[-aSize * cos(hexAngle)], [size], [aSize * sin(hexAngle)], [1.0]],
							 [[-aSize], [size], [0.0], [1.0]],
							 [[-aSize * cos(hexAngle)], [size], [-aSize * sin(hexAngle)], [1.0]],
							 [[aSize * cos(hexAngle)], [size], [-aSize * sin(hexAngle)], [1.0]],
							 [[aSize], [-size], [0.0], [1.0]],										# 7: Bottom of hexagonal body...
							 [[aSize * cos(hexAngle)], [-size], [aSize * sin(hexAngle)], [1.0]],
							 [[-aSize * cos(hexAngle)], [-size], [aSize * sin(hexAngle)], [1.0]],
							 [[-aSize], [-size], [0.0], [1.0]],
							 [[-aSize * cos(hexAngle)], [-size], [-aSize * sin(hexAngle)], [1.0]],
							 [[aSize * cos(hexAngle)], [-size], [-aSize * sin(hexAngle)], [1.0]],
							 [[0.0], [-aSize - 1.1 * aSize], [0.0], [1.0]]]							# 13: apex of bottom pyramid


		# Build a matrix to transform from the canonical crystal's coordinate
		# system to global coordinates. A 3-by-3 matrix is sufficient, because
		# the origin doesn't change in going from coordinate system to the
		# other.

		rotatedX = [cos(polar) * cos(azimuth), -sin(polar), cos(polar) * sin(azimuth)]
		rotatedY = [sin(polar) * cos(azimuth), cos(polar), sin(polar) * sin(azimuth)]
		rotatedZ = [-sin(azimuth), 0.0, cos(azimuth)]

		transform = [[rotatedX[0], rotatedY[0], rotatedZ[0], position[0]],
					 [rotatedX[1], rotatedY[1], rotatedZ[1], position[1]],
					 [rotatedX[2], rotatedY[2], rotatedZ[2], position[2]],
					 [0.0, 0.0, 0.0, 1.0]]


		# Transform canonical coordinates to world ones, building actual vertex
		# objects from the transformed points.

		vertices = []

		for canonical in canonicalVertices:
			transformed = matrixMultiply(transform, canonical)
			vertices.append( Vertex( transformed[0][0], transformed[1][0], transformed[2][0] ) )


		# Build a list of the crystal's faces. I think of the crystal as having
		# 6 sides, each consisting of a rectangle from the main body of the
		# crystal and triangles from the top and bottom pyramids. So I step
		# through sides 0 through 5, accumulating lists of indices to each
		# side's faces. In finding these indices, it helps to remember that the
		# apex of the top pyramid is at index 0, and the apex of the bottom
		# pyramid at 13. Vertices around the top of the crystal's body start at
		# index 1 and proceed clockwise around the crystal as seen from the
		# top; vertices around the bottom of the body start at index 7.

		faces = []

		topApex = 0
		topStart = 1
		bottomStart = 7
		bottomApex = 13

		for i in range( 6 ) :

			nextTop = ( i + 1 ) % 6 + topStart
			nextBottom = ( i + 1 ) % 6 + bottomStart

			faces += [ [ nextTop, i + topStart, topApex ],							# Top triangle
					   [ i + bottomStart, i + topStart, nextTop, nextBottom ],		# Body rectangle
					   [ i + bottomStart, nextBottom, bottomApex ] ]				# Bottom triangle


		# Initialize the amethyst with the vertices and faces.

		amethystColor = (0.53, 0.38, 0.93, 0.55, 0.85, 50.0)

		super().__init__( vertices, faces, amethystColor )
