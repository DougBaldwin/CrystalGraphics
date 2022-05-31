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
from ConvexPolyhedron import ConvexPolyhedron
from Vertex import Vertex
from Edge import Edge
from Face import Face
from VectorOps import matrixMultiply
from math import sin, cos, pi




class Amethyst ( Polyhedron ) :
	
	
	
	
	# Initialize an amethyst, given its center point, a polar angle between the
	# z axis and its c axis, the angle between its c axis and the positive x
	# axis (specifically, the angle from the x axis towards the z axis), and
	# the distance the c axis extends either side of the center, not counting
	# the pyramids at the ends of the crystal.
	
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
		
		aSize = 0.9 * size					# Crystal's extent in the a dimensions
		hexAngle = pi / 3.0					# Radian measure of 60 degree angle between faces of hexagon
		
		
		# List the vertices of the canonical crystal. Each vertex is a column
		# vector in homogeneous coordinates, as my utility functions understand
		# such things, so I can easily change its coordinate system by matrix
		# multiplication.
		
		canonicalVertices = [ [ [0.0], [size + 1.1 * aSize], [0.0], [1.0] ],		# Apex of top pyramid
							  [ [aSize], [size], [0.0], [1.0] ],					# Start of top of hexagonal body
							  [ [aSize * cos(hexAngle)], [size], [aSize * sin(hexAngle)], [1.0] ],
							  [ [-aSize * cos(hexAngle)], [size], [aSize * sin(hexAngle)], [1.0] ],
							  [ [-aSize], [size], [0.0], [1.0] ],
							  [ [-aSize * cos(hexAngle)], [size], [-aSize * sin(hexAngle)], [1.0] ],
							  [ [aSize * cos(hexAngle)], [size], [-aSize * sin(hexAngle)], [1.0] ],
							  [ [aSize], [-size], [0.0], [1.0] ],					# Bottom of hexagonal body...
							  [ [aSize * cos(hexAngle)], [-size], [aSize * sin(hexAngle)], [1.0] ],
							  [ [-aSize * cos(hexAngle)], [-size], [aSize * sin(hexAngle)], [1.0] ],
							  [ [-aSize], [-size], [0.0], [1.0] ],
							  [ [-aSize * cos(hexAngle)], [-size], [-aSize * sin(hexAngle)], [1.0] ],
							  [ [aSize * cos(hexAngle)], [-size], [-aSize * sin(hexAngle)], [1.0] ],
							  [ [0.0], [-aSize - 1.1 * aSize], [0.0], [1.0] ] ]		# And finally apex of bottom pyramid
		
		
		# Build a matrix to transform from the canonical crystal's coordinate
		# system to global coordinates. A 3-by-3 matrix is sufficient, because
		# the origin doesn't change in going from coordinate system to the
		# other.
		
		rotatedX = [ cos(polar) * cos(azimuth), -sin(polar), cos(polar) * sin(azimuth) ]
		rotatedY = [ sin(polar) * cos(azimuth), cos(polar), sin(polar) * sin(azimuth) ]
		rotatedZ = [ -sin(azimuth), 0.0, cos(azimuth) ]
		
		transform = [ [ rotatedX[0], rotatedY[0], rotatedZ[0], position[0] ],
					  [ rotatedX[1], rotatedY[1], rotatedZ[1], position[1] ],
					  [ rotatedX[2], rotatedY[2], rotatedZ[2], position[2] ],
					  [    0.0,         0.0,         0.0,         1.0 ] ]
		
		
		# Transform canonical coordinates to world ones, building actual vertex
		# objects from the transformed points.
		
		vertices = []
		
		for canonical in canonicalVertices :
			transformed = matrixMultiply( transform, canonical )
			vertices.append( Vertex( transformed[0][0], transformed[1][0], transformed[2][0] ) )
		
		
		# Build a list of the crystal's edges. There are edges from the top
		# apex to each vertex around the top of the hexagonal prism, from each
		# of them to the corresponding vertex around the bottom, and from each
		# vertex at the bottom of the prism to the bottom apex. There are also
		# edges between consecutive vertices around the top and bottom of the
		# prism. I add these vertices to the list in groups of 5, starting with
		# the ones running from the top down the prism to the bottom, and then
		# ending with the edges around the prism from the current "slice" to
		# the next one.
		
		edges = []
		
		for i in range( 6 ) :
			edges += [ Edge( vertices[0], vertices[1+i] ),
					   Edge( vertices[1+i], vertices[7+i] ),
					   Edge( vertices[7+i], vertices[13] ),
					   Edge( vertices[1+i], vertices[ 2+i if i < 5 else 1 ] ),
					   Edge( vertices[7+i], vertices[ 8+i if i < 5 else 7 ] ) ]
		
		edgesPerGroup = 5
		topApex = 0						# Offset of edge to top apex within a group
		prismSide = 1					# Offset of vertical side down prism
		bottomApex = 2					# Offset of edge to bottom apex
		prismTop = 3					# Offset of edge across top of prism
		prismBottom = 4					# Offset of edge across bottom of prism
		
		
		# Build a list of the crystal's faces. This list consists of, for each
		# of the 6 sides of the hexagonal structure, a triangular face from the
		# top pyramid, a rectangular one from the main prism, and another
		# triangular one from the bottom pyramid.
		
		faces = []
		
		for i in range( 6 ) :
			
			leading = ( (i + 1) % 6 ) * edgesPerGroup				# Index where edges at the leading side of this face start
			trailing = i * edgesPerGroup							# Index to edges for trailing side of this face
		
			faces += [ Face( [ edges[ leading + topApex ],
							   edges[ trailing + prismTop ],
							   edges[ trailing + topApex ] ] ),
					   Face( [ edges[ trailing + prismTop ],
					   		   edges[ leading + prismSide ],
					   		   edges[ trailing + prismBottom ],
					   		   edges[ trailing + prismSide ] ] ),
					   Face( [ edges[ trailing + bottomApex ],
					   		   edges[ trailing + prismBottom ],
					   		   edges[ leading + bottomApex ] ] ) ]		
		
		
		# The actual amethyst is just 1 conves polyhedron. Create it from the
		# vertices, edges, and faces built earlier, then use it to initialize
		# the superclass.
		
		amethystColor = ( 0.53, 0.38, 0.93, 0.55, 0.85, 50.0 )
		
		convex = ConvexPolyhedron( faces, edges, vertices, amethystColor )
		
		super().__init__( [convex] )
